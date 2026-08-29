"""
Step 5: Train & evaluate XGBoost / LightGBM / CatBoost, each with and without
log1p target transform, with SHAP explainability, for ONE segment
(overall | turvo | magnus). Run separately per segment to keep runtime
bounded. Usage: python3 05_run_models.py <overall|turvo|magnus>
"""
import sys
sys.path.insert(0, "/home/claude/proj/src")
import json
import time
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

from modeling_utils import split_80_10_10, train_eval_one, TARGET

SEGMENT = sys.argv[1] if len(sys.argv) > 1 else "turvo"
DATA_DIR = "/home/claude/proj/data/processed"
ART_DIR = "/home/claude/proj/artifacts"
MODEL_DIR = "/home/claude/proj/artifacts/models"
import os
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(f"{ART_DIR}/shap", exist_ok=True)

FILE_MAP = {
    "overall": f"{DATA_DIR}/veltris_overall.parquet",
    "turvo": f"{DATA_DIR}/veltris_reduced.parquet",
    "magnus": f"{DATA_DIR}/veltris_magnus_imputed.parquet",
}
df = pd.read_parquet(FILE_MAP[SEGMENT])
final_features = json.load(open(f"{DATA_DIR}/feature_selection_summary.json"))["final_features"]

feature_cols = list(final_features)
if SEGMENT == "overall":
    df["SourceName_is_Magnus"] = (df["SourceName"] == "Magnus").astype(int)
    feature_cols = feature_cols + ["SourceName_is_Magnus"]

print(f"=== Segment: {SEGMENT} | shape={df.shape} | features={len(feature_cols)} ===")

strat_col = "SourceName" if SEGMENT == "overall" else None
train, val, test = split_80_10_10(df, stratify_col=strat_col)
print(f"Train={len(train)} Val={len(val)} Test={len(test)} "
      f"({len(train)/len(df)*100:.0f}/{len(val)/len(df)*100:.0f}/{len(test)/len(df)*100:.0f})")

results = []
shap_importances = {}

for algo in ["XGBoost", "LightGBM", "CatBoost"]:
    for log_tf in [False, True]:
        tag = f"{algo}_{'log1p' if log_tf else 'raw'}"
        t0 = time.time()
        model, metrics, shap_values, shap_sample, mean_abs_shap = train_eval_one(
            algo, feature_cols, train, val, test, log_transform=log_tf
        )
        elapsed = time.time() - t0
        print(f"  {tag}: MAE={metrics['MAE']:.1f} RMSE={metrics['RMSE']:.1f} "
              f"MAPE={metrics['MAPE']:.1f}% R2={metrics['R2']:.3f} ({elapsed:.1f}s)", flush=True)
        row = {"segment": SEGMENT, "algorithm": algo,
               "target_transform": "log1p" if log_tf else "raw", **metrics}
        results.append(row)
        shap_importances[tag] = mean_abs_shap.to_dict()

        # save SHAP summary plot
        if shap_values is not None:
            plt.figure()
            shap.summary_plot(shap_values, shap_sample, show=False, max_display=15)
            plt.title(f"SHAP summary - {SEGMENT} - {tag}")
            plt.tight_layout()
            plt.savefig(f"{ART_DIR}/shap/shap_{SEGMENT}_{tag}.png", dpi=120, bbox_inches="tight")
            plt.close()

        # persist model
        with open(f"{MODEL_DIR}/{SEGMENT}_{tag}.pkl", "wb") as f:
            pickle.dump(model, f)

res_df = pd.DataFrame(results)
res_df.to_csv(f"{ART_DIR}/model_performance_{SEGMENT}.csv", index=False)
with open(f"{ART_DIR}/shap_importance_{SEGMENT}.json", "w") as f:
    json.dump(shap_importances, f, indent=2)

print(res_df.to_string(index=False))
print(f"DONE segment={SEGMENT}")
