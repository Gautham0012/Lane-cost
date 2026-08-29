"""
Step 1: Load raw data, compute descriptive statistics on the RAW dataset,
clean it (drop near-empty / leakage / high-cardinality-ID columns, drop
duplicate rows, drop rows with missing values, remove outliers on key
continuous columns via IQR), then compute descriptive statistics on the
PROCESSED dataset. Saves both stats tables and the cleaned dataframe.
"""
import pandas as pd
import numpy as np
import json
import time

t0 = time.time()
RAW_CSV = "/home/claude/raw_data.csv"
OUT_DIR = "/home/claude/proj/data/processed"

df = pd.read_csv(RAW_CSV, low_memory=False)
print("Raw shape:", df.shape)

# ---------------------------------------------------------------------
# 0. Convert Excel-serial date columns to real datetimes
# ---------------------------------------------------------------------
DATE_COLS = ["CreationDate", "FirstPickup", "LastPickup",
             "FirstScheduledDelivery", "LastScheduledDelivery",
             "FirstDelivery", "LastDelivery"]
for c in DATE_COLS:
    df[c] = pd.to_datetime(df[c], unit="D", origin="1899-12-30", errors="coerce")

# ---------------------------------------------------------------------
# 1. Descriptive statistics on the ENTIRE (raw) dataset
# ---------------------------------------------------------------------
num_cols_raw = df.select_dtypes(include=[np.number]).columns.tolist()
desc_raw_numeric = df[num_cols_raw].describe().T
desc_raw_numeric["missing_pct"] = df[num_cols_raw].isna().mean().values * 100
desc_raw_numeric["skew"] = df[num_cols_raw].skew().values
desc_raw_numeric["kurtosis"] = df[num_cols_raw].kurtosis().values

cat_cols_raw = df.select_dtypes(include=["object"]).columns.tolist()
desc_raw_cat = pd.DataFrame({
    "n_unique": df[cat_cols_raw].nunique(),
    "missing_pct": df[cat_cols_raw].isna().mean() * 100,
    "top_value": df[cat_cols_raw].mode().iloc[0] if len(cat_cols_raw) else None,
})

desc_raw_numeric.to_csv(f"{OUT_DIR}/descriptive_stats_RAW_numeric.csv")
desc_raw_cat.to_csv(f"{OUT_DIR}/descriptive_stats_RAW_categorical.csv")
print("Raw descriptive stats saved.")

# ---------------------------------------------------------------------
# 2. Drop columns that are not usable features
#    (near-empty >50% missing, direct target leakage, raw high-card IDs,
#     absolute calendar dates already represented by engineered features,
#     the vendor-provided Split column since we build our own split)
# ---------------------------------------------------------------------
DROP_NEAR_EMPTY = ["InoperableAny", "NetWidth", "OriginTimeZone", "DestinationTimeZone"]
DROP_LEAKAGE = ["TotalCostLog"]  # direct transform of the target
DROP_HIGH_CARD_ID = ["OriginPostalCode", "DestinationPostalCode", "OriginCity", "DestinationCity"]
DROP_RAW_DATES = ["FirstPickup", "LastPickup", "FirstScheduledDelivery",
                   "LastScheduledDelivery", "FirstDelivery", "LastDelivery", "CreationDate"]
DROP_META = ["Split", "ShipmentId"]

drop_cols = DROP_NEAR_EMPTY + DROP_LEAKAGE + DROP_HIGH_CARD_ID + DROP_RAW_DATES + DROP_META
drop_cols = [c for c in drop_cols if c in df.columns]
df_clean = df.drop(columns=drop_cols)
print(f"Dropped {len(drop_cols)} unusable columns:", drop_cols)

# ---------------------------------------------------------------------
# 3. Remove duplicate rows
# ---------------------------------------------------------------------
n_before = len(df_clean)
df_clean = df_clean.drop_duplicates()
print(f"Duplicate rows removed: {n_before - len(df_clean)}")

# ---------------------------------------------------------------------
# 4. Remove rows with missing values (in the retained feature columns)
# ---------------------------------------------------------------------
n_before = len(df_clean)
df_clean = df_clean.dropna(axis=0, how="any")
print(f"Rows dropped for missing values: {n_before - len(df_clean)} "
      f"({(n_before - len(df_clean)) / n_before * 100:.1f}%)")

# ---------------------------------------------------------------------
# 5. Outlier removal (IQR rule, 1.5x) on target + key continuous drivers
# ---------------------------------------------------------------------
OUTLIER_COLS = ["TotalCost", "TotalMiles", "TotalWeight", "HaversineMiles"]
outlier_report = {}
n_before = len(df_clean)
mask = pd.Series(True, index=df_clean.index)
for c in OUTLIER_COLS:
    q1, q3 = df_clean[c].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    col_mask = df_clean[c].between(lo, hi)
    outlier_report[c] = {
        "lower_bound": float(lo), "upper_bound": float(hi),
        "n_outliers_removed": int((~col_mask).sum())
    }
    mask &= col_mask
df_clean = df_clean[mask].reset_index(drop=True)
print(f"Outlier rows removed (IQR, target+key drivers): {n_before - len(df_clean)} "
      f"({(n_before - len(df_clean)) / n_before * 100:.1f}%)")
print(json.dumps(outlier_report, indent=2))

with open(f"{OUT_DIR}/outlier_report.json", "w") as f:
    json.dump(outlier_report, f, indent=2)

print("Processed shape:", df_clean.shape)

# ---------------------------------------------------------------------
# 6. Descriptive statistics on the PROCESSED dataset
# ---------------------------------------------------------------------
num_cols_p = df_clean.select_dtypes(include=[np.number]).columns.tolist()
desc_p_numeric = df_clean[num_cols_p].describe().T
desc_p_numeric["missing_pct"] = df_clean[num_cols_p].isna().mean().values * 100
desc_p_numeric["skew"] = df_clean[num_cols_p].skew().values
desc_p_numeric["kurtosis"] = df_clean[num_cols_p].kurtosis().values

cat_cols_p = df_clean.select_dtypes(include=["object"]).columns.tolist()
desc_p_cat = pd.DataFrame({
    "n_unique": df_clean[cat_cols_p].nunique(),
    "missing_pct": df_clean[cat_cols_p].isna().mean() * 100,
    "top_value": df_clean[cat_cols_p].mode().iloc[0] if len(cat_cols_p) else None,
})

desc_p_numeric.to_csv(f"{OUT_DIR}/descriptive_stats_PROCESSED_numeric.csv")
desc_p_cat.to_csv(f"{OUT_DIR}/descriptive_stats_PROCESSED_categorical.csv")

# ---------------------------------------------------------------------
# 7. Persist
# ---------------------------------------------------------------------
df_clean.to_parquet(f"{OUT_DIR}/veltris_cleaned.parquet", index=False)

summary = {
    "raw_shape": list(df.shape),
    "processed_shape": list(df_clean.shape),
    "columns_dropped_unusable": drop_cols,
    "rows_dropped_duplicates": int(n_before) - int(n_before),  # placeholder overwritten below
}
summary["outlier_report"] = outlier_report
with open(f"{OUT_DIR}/preprocessing_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("DONE preprocessing in", round(time.time() - t0, 1), "s")
