"""
Step 4: Build the three modeling datasets on the SAME final (VIF+Boruta)
reduced feature set:
  - Turvo  : already fully clean (rows dropped for missing values upstream)
  - Magnus : same cleaning (dedup + outlier IQR on target/key drivers) BUT
             missing values are IMPUTED (median/mode) instead of dropped,
             because Magnus rows are almost entirely lost under listwise
             deletion (EquipmentType/Enclosed are 100% missing for Magnus).
  - Overall: Turvo (clean) + Magnus (imputed) concatenated, with SourceName
             kept as an explicit Carrier-group feature.
"""
import pandas as pd
import numpy as np
import json

RAW_CSV = "/home/claude/raw_data.csv"
DATA_DIR = "/home/claude/proj/data/processed"
TARGET = "TotalCost"

final_features = json.load(open(f"{DATA_DIR}/feature_selection_summary.json"))["final_features"]
KEEP_COLS = final_features + ["SourceName", TARGET]

# ---------------------------------------------------------------------
# Turvo (already-clean reduced dataset)
# ---------------------------------------------------------------------
turvo_df = pd.read_parquet(f"{DATA_DIR}/veltris_reduced.parquet")
turvo_df["SourceName"] = "Turvo"
print("Turvo:", turvo_df.shape)

# ---------------------------------------------------------------------
# Magnus - rebuild from raw with the SAME column-drop / dedup / outlier
# logic as 01_preprocessing.py, but impute instead of dropping rows.
# ---------------------------------------------------------------------
raw = pd.read_csv(RAW_CSV, low_memory=False)
mag = raw[raw["SourceName"] == "Magnus"].copy()
print("Magnus raw:", mag.shape)

DATE_COLS = ["CreationDate", "FirstPickup", "LastPickup",
             "FirstScheduledDelivery", "LastScheduledDelivery",
             "FirstDelivery", "LastDelivery"]
for c in DATE_COLS:
    mag[c] = pd.to_datetime(mag[c], unit="D", origin="1899-12-30", errors="coerce")

DROP_NEAR_EMPTY = ["InoperableAny", "NetWidth", "OriginTimeZone", "DestinationTimeZone"]
DROP_LEAKAGE = ["TotalCostLog"]
DROP_HIGH_CARD_ID = ["OriginPostalCode", "DestinationPostalCode", "OriginCity", "DestinationCity"]
DROP_RAW_DATES = DATE_COLS
DROP_META = ["Split", "ShipmentId"]
drop_cols = [c for c in DROP_NEAR_EMPTY + DROP_LEAKAGE + DROP_HIGH_CARD_ID + DROP_RAW_DATES + DROP_META
             if c in mag.columns]
mag = mag.drop(columns=drop_cols)

n0 = len(mag)
mag = mag.drop_duplicates()
print(f"Magnus duplicates removed: {n0 - len(mag)}")

# Outlier removal only where the bound columns exist and aren't fully null
n0 = len(mag)
mask = pd.Series(True, index=mag.index)
outlier_report_mag = {}
for c in ["TotalCost", "TotalMiles", "TotalWeight", "HaversineMiles"]:
    if c in mag.columns and mag[c].notna().sum() > 10:
        q1, q3 = mag[c].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        col_mask = mag[c].between(lo, hi) | mag[c].isna()
        outlier_report_mag[c] = {"lower_bound": float(lo), "upper_bound": float(hi),
                                  "n_removed": int((~col_mask).sum())}
        mask &= col_mask
mag = mag[mask].reset_index(drop=True)
print(f"Magnus outlier rows removed: {n0 - len(mag)}")
# Magnus rows must still have the TARGET itself present (can't impute the label)
mag = mag[mag[TARGET].notna()].reset_index(drop=True)

# Keep only columns needed downstream (final selected features + SourceName + target)
missing_needed = [c for c in KEEP_COLS if c not in mag.columns]
print("Columns needed but absent in Magnus raw (unexpected):", missing_needed)
mag_model = mag[[c for c in KEEP_COLS if c in mag.columns]].copy()

# ---------------------------------------------------------------------
# Imputation (median for numeric, mode for categorical) - fit on Magnus data
# ---------------------------------------------------------------------
impute_values = {}
for c in mag_model.columns:
    if c == TARGET:
        continue
    if mag_model[c].isna().any():
        if mag_model[c].dtype == "object":
            fill = mag_model[c].mode(dropna=True)
            fill = fill.iloc[0] if len(fill) else "Unknown"
        else:
            fill = mag_model[c].median()
        impute_values[c] = fill
        mag_model[c] = mag_model[c].fillna(fill)

with open(f"{DATA_DIR}/magnus_imputation_values.json", "w") as f:
    json.dump({k: (v if not isinstance(v, (np.floating, np.integer)) else float(v))
               for k, v in impute_values.items()}, f, indent=2, default=str)

print("Magnus imputed columns:", list(impute_values.keys()))
print("Magnus final modeling shape:", mag_model.shape)
mag_model.to_parquet(f"{DATA_DIR}/veltris_magnus_imputed.parquet", index=False)

# ---------------------------------------------------------------------
# Overall = Turvo + Magnus(imputed), aligned columns
# ---------------------------------------------------------------------
common_cols = [c for c in KEEP_COLS if c in turvo_df.columns and c in mag_model.columns]
overall_df = pd.concat([turvo_df[common_cols], mag_model[common_cols]], ignore_index=True)
overall_df.to_parquet(f"{DATA_DIR}/veltris_overall.parquet", index=False)
print("Overall combined shape:", overall_df.shape)
print(overall_df["SourceName"].value_counts())

summary = {
    "turvo_shape": list(turvo_df.shape),
    "magnus_raw_shape": [int(raw[raw['SourceName']=='Magnus'].shape[0]), int(raw.shape[1])],
    "magnus_after_cleaning_outliers_shape": list(mag.shape),
    "magnus_imputed_columns": list(impute_values.keys()),
    "magnus_model_shape": list(mag_model.shape),
    "overall_shape": list(overall_df.shape),
    "magnus_outlier_report": outlier_report_mag,
}
with open(f"{DATA_DIR}/segment_dataset_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("DONE")
