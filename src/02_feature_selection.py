"""
Step 2: Multicollinearity check (VIF) + Boruta all-relevant feature selection.
Produces the final REDUCED feature set and the reduced dataset used for modeling.
"""
import pandas as pd
import numpy as np
import json
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from boruta import BorutaPy

t0 = time.time()
DATA = "/home/claude/proj/data/processed/veltris_cleaned.parquet"
OUT_DIR = "/home/claude/proj/data/processed"
TARGET = "TotalCost"

df = pd.read_parquet(DATA)
print("Loaded:", df.shape)

id_like = ["SourceName"]  # constant post-cleaning (Turvo only) - not predictive, kept aside
cat_cols = [c for c in df.select_dtypes(include="object").columns if c not in id_like]
num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != TARGET]

print("Categorical:", cat_cols)
print("Numeric candidate features:", len(num_cols))

# ---------------------------------------------------------------------
# 1. VIF on numeric predictors (sampled for speed, standardized)
# ---------------------------------------------------------------------
rng = np.random.RandomState(42)
sample_idx = rng.choice(df.index, size=min(20000, len(df)), replace=False)
X_num = df.loc[sample_idx, num_cols].astype(float)
stds = X_num.std()
zero_var_cols = stds[stds < 1e-8].index.tolist()
if zero_var_cols:
    print("Dropping zero-variance columns before VIF:", zero_var_cols)
    num_cols = [c for c in num_cols if c not in zero_var_cols]
    X_num = X_num.drop(columns=zero_var_cols)
X_num = (X_num - X_num.mean()) / (X_num.std() + 1e-9)
X_num = X_num.fillna(0)

def compute_vif_fast(X):
    """VIF via inverse of the correlation matrix (diagonal) - O(p^3) once per
    call instead of p separate OLS regressions. Equivalent result to
    statsmodels.variance_inflation_factor on standardized data."""
    corr = np.corrcoef(X.values, rowvar=False)
    corr += np.eye(corr.shape[0]) * 1e-8  # ridge for numerical stability
    inv = np.linalg.pinv(corr)
    vifs = np.diag(inv)
    return pd.Series(vifs, index=X.columns)

VIF_THRESHOLD = 10.0
dropped_vif = []
X_iter = X_num.copy()
vif_history = []
it = 0
while X_iter.shape[1] > 1:
    it += 1
    vifs = compute_vif_fast(X_iter)
    worst = vifs.idxmax()
    vif_history.append(float(vifs.max()))
    print(f"  VIF iter {it}: {X_iter.shape[1]} features, max VIF = {vifs.max():.1f} ({worst})", flush=True)
    if vifs.max() > VIF_THRESHOLD:
        dropped_vif.append((worst, float(vifs.max())))
        X_iter = X_iter.drop(columns=[worst])
    else:
        break

final_vif = compute_vif_fast(X_iter)
vif_survivors = final_vif.index.tolist()
print(f"VIF elimination: dropped {len(dropped_vif)} of {len(num_cols)} numeric features "
      f"(threshold={VIF_THRESHOLD})")

pd.DataFrame(dropped_vif, columns=["feature", "vif_at_removal"]).to_csv(
    f"{OUT_DIR}/vif_dropped_features.csv", index=False)
final_vif.sort_values(ascending=False).to_csv(f"{OUT_DIR}/vif_final_scores.csv")
with open(f"{OUT_DIR}/vif_survivors.json", "w") as f:
    json.dump(vif_survivors, f)
print("VIF stage done at", round(time.time()-t0,1), "s -- survivors:", len(vif_survivors))

import sys
if "--vif-only" in sys.argv:
    sys.exit(0)

# ---------------------------------------------------------------------
# 2. Boruta all-relevant feature selection (on VIF survivors + encoded cats)
# ---------------------------------------------------------------------
boruta_candidates = vif_survivors + cat_cols
boruta_sample_idx = rng.choice(df.index, size=min(8000, len(df)), replace=False)
X_bor = df.loc[boruta_sample_idx, boruta_candidates].copy()
y_bor = df.loc[boruta_sample_idx, TARGET].values

encoders = {}
for c in cat_cols:
    le = LabelEncoder()
    X_bor[c] = le.fit_transform(X_bor[c].astype(str))
    encoders[c] = le
X_bor = X_bor.fillna(X_bor.median(numeric_only=True)).values.astype(float)

print(f"Boruta: {X_bor.shape[0]} rows x {X_bor.shape[1]} candidate features", flush=True)
rf = RandomForestRegressor(n_estimators=40, max_depth=5, n_jobs=1, random_state=42)
boruta_selector = BorutaPy(rf, n_estimators=40, max_iter=12, random_state=42, verbose=2)
boruta_selector.fit(X_bor, y_bor)

boruta_result = pd.DataFrame({
    "feature": boruta_candidates,
    "confirmed": boruta_selector.support_,
    "tentative": boruta_selector.support_weak_,
    "ranking": boruta_selector.ranking_,
}).sort_values("ranking")
boruta_result.to_csv(f"{OUT_DIR}/boruta_results.csv", index=False)
print(boruta_result.to_string())

boruta_selected = boruta_result.loc[
    boruta_result["confirmed"] | boruta_result["tentative"], "feature"
].tolist()

# ---------------------------------------------------------------------
# 3. Final reduced feature set = Boruta-selected features (already VIF-clean)
#    Always retain SourceName (segment key) + TARGET even if not selected.
# ---------------------------------------------------------------------
final_features = boruta_selected
reduced_cols = list(dict.fromkeys(final_features + ["SourceName", TARGET]))
reduced_df = df[reduced_cols].copy()
reduced_df.to_parquet(f"{OUT_DIR}/veltris_reduced.parquet", index=False)
reduced_df.to_csv(f"{OUT_DIR}/veltris_reduced.csv", index=False)

print("Final reduced feature count:", len(final_features))
print("Reduced dataset shape:", reduced_df.shape)

summary = {
    "n_numeric_candidates": len(num_cols),
    "n_dropped_by_vif": len(dropped_vif),
    "vif_dropped_features": [d[0] for d in dropped_vif],
    "n_boruta_candidates": len(boruta_candidates),
    "n_boruta_confirmed": int(boruta_result["confirmed"].sum()),
    "n_boruta_tentative": int(boruta_result["tentative"].sum()),
    "final_features": final_features,
    "final_feature_count": len(final_features),
    "reduced_shape": list(reduced_df.shape),
}
with open(f"{OUT_DIR}/feature_selection_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("DONE feature selection in", round(time.time() - t0, 1), "s")
