# Veltris Vehicle Shipment Cost Modeling

End-to-end pipeline that cleans the Veltris vehicle-shipment dataset, reduces its
dimensionality (VIF + Boruta), explores feature/target relationships, and trains
XGBoost / LightGBM / CatBoost cost-prediction models (with and without a `log1p`
target transform, with SHAP explainability) - **overall** and **separately per
carrier-source segment** (`Turvo`, `Magnus`).

## Repository layout

```
├── data/
│   └── processed/                      # all intermediate + final tabular outputs
│       ├── descriptive_stats_RAW_*.csv         # descriptive stats: entire raw dataset
│       ├── descriptive_stats_PROCESSED_*.csv   # descriptive stats: cleaned dataset
│       ├── outlier_report.json
│       ├── preprocessing_summary.json
│       ├── veltris_cleaned.parquet             # post-cleaning, pre-dimensionality-reduction
│       ├── vif_dropped_features.csv / vif_final_scores.csv / vif_survivors.json
│       ├── boruta_results.csv
│       ├── feature_selection_summary.json      # final 24-feature list
│       ├── final_feature_group_mapping.csv     # feature -> business group
│       ├── veltris_reduced.parquet / .csv      # REDUCED DATASET (Turvo, cleaned)
│       ├── magnus_imputation_values.json
│       ├── veltris_magnus_imputed.parquet      # Magnus, imputed (not dropped)
│       ├── veltris_overall.parquet             # Turvo + Magnus combined
│       └── segment_dataset_summary.json
├── notebooks/
│   ├── 01_data_preprocessing_eda.ipynb         # load, clean, descriptive stats, EDA
│   ├── 02_feature_selection_vif_boruta.ipynb   # VIF + Boruta, feature groups
│   ├── 03_segment_datasets.ipynb               # Magnus imputation + overall build
│   └── 04_modeling_shap_evaluation.ipynb       # 18-model train/eval/SHAP + comparison
├── src/                                        # the actual scripts the notebooks are built from
│   ├── feature_groups.py                       # feature -> group taxonomy + rationale
│   ├── xml_to_csv.py                           # fast raw .xlsx -> .csv streaming converter
│   ├── 01_preprocessing.py
│   ├── 02_feature_selection.py
│   ├── 03_eda_visualization.py
│   ├── 04_build_segment_datasets.py
│   ├── modeling_utils.py                       # split / train / SHAP / metrics helpers
│   └── 05_run_models.py                        # per-segment model runner (CLI: overall|turvo|magnus)
├── artifacts/
│   ├── figures/                                # EDA + model-comparison PNGs
│   ├── shap/                                   # 18 SHAP summary-plot PNGs
│   ├── models/                                 # 18 pickled trained models
│   ├── model_performance_<segment>.csv         # per-segment metrics
│   ├── model_performance_ALL.csv               # master 18-row comparison table
│   └── shap_importance_<segment>.json          # mean |SHAP| per feature per model
├── reports/
│   ├── Veltris_Vehicle_Cost_Model_Summary.docx
│   └── Veltris_Vehicle_Cost_Model_Summary.pptx
├── requirements.txt
└── README.md
```

## How to reproduce

```bash
pip install -r requirements.txt

# 1. Convert the raw .xlsx (very large) to CSV once
python3 src/xml_to_csv.py

# 2. Preprocessing + descriptive stats
python3 src/01_preprocessing.py

# 3. VIF + Boruta feature selection -> reduced dataset
python3 src/02_feature_selection.py

# 4. EDA & visualization
python3 src/03_eda_visualization.py

# 5. Build segment datasets (Turvo / Magnus-imputed / Overall)
python3 src/04_build_segment_datasets.py

# 6. Train + evaluate + SHAP, per segment
python3 src/05_run_models.py overall
python3 src/05_run_models.py turvo
python3 src/05_run_models.py magnus
```

Or open the four notebooks in `notebooks/` in order - they contain the same code with
narrative explanation and captured outputs.

## Headline results

| Segment | Best model | MAE ($) | RMSE ($) | MAPE (%) | R2 |
|---|---|---|---|---|---|
| Overall | XGBoost (raw target) | 85.9 | 147.1 | 21.0 | 0.947 |
| Turvo   | XGBoost (raw target) | 87.3 | 148.9 | 20.2 | 0.949 |
| Magnus  | LightGBM (raw target) | 59.9 | 112.7 | 20.7 | 0.860 |

Full 18-model comparison (3 algorithms x raw/log1p x 3 segments) in
`artifacts/model_performance_ALL.csv` and `reports/Veltris_Vehicle_Cost_Model_Summary.docx`.

## Data notes

- Source file: `Veltris-Vehicle.xlsx` (305,838 rows x 145 columns). It is **not** committed to
  this repository (too large for GitHub's default limits) - place it locally and run
  `src/xml_to_csv.py` to regenerate `raw_data.csv`.
- Target variable: `TotalCost` (USD).
- Segments: `SourceName` = `Turvo` (287,860 raw rows) / `Magnus` (17,978 raw rows).
