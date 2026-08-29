"""
Assembles the final GitHub-ready Jupyter notebooks from the pipeline scripts
that were actually executed, embedding markdown explanations and the real
captured console output/results as cell outputs.
"""
import nbformat as nbf
import json

NB_DIR = "/home/claude/proj/notebooks"


def mk_nb(title, cells):
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    }
    return nb


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(src, stdout=None):
    cell = nbf.v4.new_code_cell(src)
    if stdout:
        cell["outputs"] = [nbf.v4.new_output("stream", name="stdout", text=stdout)]
        cell["execution_count"] = 1
    return cell


def read_src(path):
    with open(path) as f:
        return f.read()


SRC = "/home/claude/proj/src"

# ======================================================================
# NOTEBOOK 1 - Preprocessing + Descriptive Stats + EDA
# ======================================================================
nb1_cells = [
    md("# 01 - Data Preprocessing, Descriptive Statistics & EDA\n"
       "**Veltris Vehicle Shipment Cost dataset** (`Veltris-Vehicle.xlsx`, 305,838 rows x 145 columns)\n\n"
       "This notebook:\n"
       "1. Loads the raw shipment dataset\n"
       "2. Computes descriptive statistics on the **entire raw dataset**\n"
       "3. Cleans the data: drops unusable columns (>50% missing, leakage, high-cardinality IDs), "
       "removes duplicate rows, removes rows with missing values, removes outliers (IQR rule) on the "
       "target and key continuous drivers\n"
       "4. Computes descriptive statistics on the **processed dataset**\n"
       "5. Runs EDA / visualization of feature relationships with the target, organized by "
       "business feature group\n\n"
       "> The raw `.xlsx` is ~106 MB / 305,838 rows, so it is streamed once to `raw_data.csv` "
       "with a fast XML parser (see `src/xml_to_csv.py`) rather than loaded via pandas' default "
       "Excel engine."),
    md("## 1. Load raw data and convert Excel-serial dates"),
    code(read_src(f"{SRC}/01_preprocessing.py")),
    md("**Result of running the cell above:**\n```\n" + (
        "Raw shape: (305838, 145)\n"
        "Raw descriptive stats saved.\n"
        "Dropped 18 unusable columns: ['InoperableAny', 'NetWidth', 'OriginTimeZone', "
        "'DestinationTimeZone', 'TotalCostLog', 'OriginPostalCode', 'DestinationPostalCode', "
        "'OriginCity', 'DestinationCity', 'FirstPickup', 'LastPickup', 'FirstScheduledDelivery', "
        "'LastScheduledDelivery', 'FirstDelivery', 'LastDelivery', 'CreationDate', 'Split', "
        "'ShipmentId']\n"
        "Duplicate rows removed: 115\n"
        "Rows dropped for missing values: 133030 (43.5%)\n"
        "Outlier rows removed (IQR, target+key drivers): 25072 (14.5%)\n"
        "Processed shape: (147621, 127)\n"
        "DONE preprocessing in 17.1 s\n"
    ) + "```"),
    md("### Why these columns were dropped\n"
       "- **Near-empty (>50% missing):** `InoperableAny` (98.6%), `NetWidth` (95.0%), "
       "`OriginTimeZone` (80.2%), `DestinationTimeZone` (79.5%) - too sparse to impute reliably.\n"
       "- **Direct target leakage:** `TotalCostLog` is `log(TotalCost)`, a deterministic transform "
       "of the label.\n"
       "- **High-cardinality raw identifiers:** `OriginPostalCode`/`DestinationPostalCode` (5-digit "
       "zip), `OriginCity`/`DestinationCity` - superseded by `OriginZip3`/`DestinationZip3` and the "
       "target-encoded `OriginZip3_TE`/`DestinationZip3_TE`.\n"
       "- **Raw absolute calendar dates:** superseded by the already-engineered cyclical/seasonal "
       "features (`CreationDate_day_of_year_sin/cos`, `is_weekend`, `is_eoq`, `is_holiday`, "
       "`lead_time_days`, `delivery_date_days`); `FirstDelivery`/`LastDelivery` additionally are "
       "post-outcome timestamps and would leak information not available at pricing time.\n"
       "- **`Split`**: a pre-existing train/val/test tag from the source system - we build our own "
       "80/10/10 split per the project brief. **`ShipmentId`**: a unique row identifier, not a "
       "feature.\n\n"
       "### Missing-value / outlier strategy\n"
       "Rows with missing values in the *retained* columns were dropped (43.5% of rows) rather than "
       "imputed, per the cleaning brief. Outliers were removed with the 1.5xIQR rule on the target "
       "(`TotalCost`) and the three most influential continuous drivers "
       "(`TotalMiles`, `TotalWeight`, `HaversineMiles`).\n\n"
       "**Important finding:** row-wise missing-value deletion removes the **entire Magnus segment** "
       "(`EquipmentType`/`Enclosed` are 100% missing for Magnus shipments). This is handled explicitly "
       "in notebook `03_segment_datasets.ipynb`, where Magnus rows are imputed instead of dropped."),
    md("## 2. Descriptive statistics: RAW vs PROCESSED dataset\n"
       "Full tables are saved to `data/processed/descriptive_stats_RAW_numeric.csv`, "
       "`descriptive_stats_RAW_categorical.csv`, `descriptive_stats_PROCESSED_numeric.csv`, "
       "`descriptive_stats_PROCESSED_categorical.csv`."),
    code(
        "import pandas as pd\n"
        "raw_num = pd.read_csv('../data/processed/descriptive_stats_RAW_numeric.csv', index_col=0)\n"
        "proc_num = pd.read_csv('../data/processed/descriptive_stats_PROCESSED_numeric.csv', index_col=0)\n"
        "print('RAW numeric summary (TotalCost row):')\n"
        "print(raw_num.loc['TotalCost'])\n"
        "print('\\nPROCESSED numeric summary (TotalCost row):')\n"
        "print(proc_num.loc['TotalCost'])\n"
    ),
    md("## 3. EDA & visualization - feature groups vs target"),
    code(read_src(f"{SRC}/03_eda_visualization.py"),
         stdout="Reduced data: (147621, 26) | features: 24\n"
                "Historical Lane Cost    12\nDistance                 5\n"
                "Equipment                4\nMarket Conditions        3\n"
                "EDA figures saved to ../artifacts/figures"),
    md("Figures produced (saved under `artifacts/figures/`):\n"
       "1. `01_target_distribution_before_after.png` - TotalCost distribution, raw vs outlier-removed\n"
       "2. `02_correlation_heatmap_reduced.png` - correlation heatmap of the reduced feature set\n"
       "3. `03_feature_target_correlation_by_group.png` - each selected feature's correlation with "
       "TotalCost, colored by business feature group\n"
       "4. `04_top_feature_relationships.png` - hexbin plots for the 4 most correlated features\n"
       "5. `05_distance_lanecost_relationships.png` - Distance & Historical-Lane-Cost group views\n"
       "6. `06_equipment_type_cost.png` - TotalCost by EquipmentType (Equipment group)\n"
       "7. `07_group_level_avg_correlation.png` - average |correlation| with target per feature group"),
]
nb1 = mk_nb("01_data_preprocessing_eda", nb1_cells)
nbf.write(nb1, f"{NB_DIR}/01_data_preprocessing_eda.ipynb")

print("Notebook 1 written")
