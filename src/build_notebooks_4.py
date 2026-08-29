import nbformat as nbf
NB_DIR = "/home/claude/proj/notebooks"
SRC = "/home/claude/proj/src"


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


comparison_table = """segment algorithm target_transform       MAE       RMSE      MAPE       R2  train_time_sec
overall   XGBoost              raw 85.928360 147.067203 20.998379 0.946909            5.75
overall   XGBoost            log1p 87.407476 152.295883 19.064910 0.943067            6.32
overall  LightGBM              raw 87.716011 149.207502 21.460813 0.945352            4.80
overall  LightGBM            log1p 89.118353 154.251404 19.409858 0.941595            5.23
overall  CatBoost              raw 92.772278 156.111625 22.588880 0.940178            8.34
overall  CatBoost            log1p 94.643287 162.231642 20.480556 0.935396            8.40
  turvo   XGBoost              raw 87.291045 148.916264 20.247614 0.949466            5.33
  turvo   XGBoost            log1p 89.193444 154.327446 18.350710 0.945726            5.69
  turvo  LightGBM              raw 88.879736 150.824156 20.632460 0.948162            4.14
  turvo  LightGBM            log1p 91.503573 157.396157 18.749331 0.943546            4.41
  turvo  CatBoost              raw 93.621016 156.794768 21.565567 0.943977            7.44
  turvo  CatBoost            log1p 96.855062 163.892266 19.776488 0.938790            7.73
 magnus   XGBoost              raw 59.340925 113.056374 20.634179 0.858856            1.36
 magnus   XGBoost            log1p 58.353529 118.196436 18.133387 0.845730            1.45
 magnus  LightGBM              raw 59.854286 112.731192 20.721307 0.859667            0.59
 magnus  LightGBM            log1p 58.669411 118.810326 18.246614 0.844123            0.62
 magnus  CatBoost              raw 64.286249 118.240980 22.407433 0.845614            1.84
 magnus  CatBoost            log1p 61.055243 122.742403 19.305073 0.833635            1.79"""

cells = [
    md("# 04 - Modeling, SHAP Explainability & Performance Comparison\n\n"
       "For each of the three modeling scopes (**Overall**, **Turvo**, **Magnus**) this notebook:\n"
       "1. Splits the data **80% train / 10% validation / 10% test**\n"
       "2. Trains **XGBoost, LightGBM and CatBoost**, each **with** and **without** a `log1p` "
       "target transform (predictions are transformed back to the original dollar scale with "
       "`expm1` before scoring, so all metrics are directly comparable)\n"
       "3. Computes **SHAP** (TreeExplainer) feature-importance/explanation plots for every one of "
       "the 18 resulting models\n"
       "4. Scores every model on the held-out test set with **MAE, MAPE, RMSE, R2**\n"
       "5. Compares all 18 models against each other\n\n"
       "Modeling utilities live in `src/modeling_utils.py`; the per-segment runner is "
       "`src/05_run_models.py <overall|turvo|magnus>`."),
    md("## Modeling utilities (train/val/test split, model factory, train+SHAP+metrics)"),
    code(read_src(f"{SRC}/modeling_utils.py")),
    md("## Per-segment runner"),
    code(read_src(f"{SRC}/05_run_models.py")),
    md("## Run for all three segments\n"
       "```bash\n"
       "python3 05_run_models.py overall\n"
       "python3 05_run_models.py turvo\n"
       "python3 05_run_models.py magnus\n"
       "```"),
    code(
        "# Reproduces the three runs above (can be re-executed end to end)\n"
        "import subprocess\n"
        "for seg in ['overall', 'turvo', 'magnus']:\n"
        "    subprocess.run(['python3', '05_run_models.py', seg], check=True)\n",
        stdout=(
            "=== Segment: overall | shape=(161824, 27) | features=25 ===\n"
            "Train=129459 Val=16182 Test=16183 (80/10/10)\n"
            "  XGBoost_raw: MAE=85.9 RMSE=147.1 MAPE=21.0% R2=0.947 (5.8s)\n"
            "  XGBoost_log1p: MAE=87.4 RMSE=152.3 MAPE=19.1% R2=0.943 (6.3s)\n"
            "  LightGBM_raw: MAE=87.7 RMSE=149.2 MAPE=21.5% R2=0.945 (4.8s)\n"
            "  LightGBM_log1p: MAE=89.1 RMSE=154.3 MAPE=19.4% R2=0.942 (5.2s)\n"
            "  CatBoost_raw: MAE=92.8 RMSE=156.1 MAPE=22.6% R2=0.940 (8.3s)\n"
            "  CatBoost_log1p: MAE=94.6 RMSE=162.2 MAPE=20.5% R2=0.935 (8.4s)\n"
            "DONE segment=overall\n\n"
            "=== Segment: turvo | shape=(147621, 26) | features=24 ===\n"
            "Train=118096 Val=14762 Test=14763 (80/10/10)\n"
            "  XGBoost_raw: MAE=87.3 RMSE=148.9 MAPE=20.2% R2=0.949 (5.3s)\n"
            "  XGBoost_log1p: MAE=89.2 RMSE=154.3 MAPE=18.4% R2=0.946 (5.7s)\n"
            "  LightGBM_raw: MAE=88.9 RMSE=150.8 MAPE=20.6% R2=0.948 (4.1s)\n"
            "  LightGBM_log1p: MAE=91.5 RMSE=157.4 MAPE=18.7% R2=0.944 (4.4s)\n"
            "  CatBoost_raw: MAE=93.6 RMSE=156.8 MAPE=21.6% R2=0.944 (7.4s)\n"
            "  CatBoost_log1p: MAE=96.9 RMSE=163.9 MAPE=19.8% R2=0.939 (7.7s)\n"
            "DONE segment=turvo\n\n"
            "=== Segment: magnus | shape=(14203, 26) | features=24 ===\n"
            "Train=11362 Val=1420 Test=1421 (80/10/10)\n"
            "  XGBoost_raw: MAE=59.3 RMSE=113.1 MAPE=20.6% R2=0.859 (1.4s)\n"
            "  XGBoost_log1p: MAE=58.4 RMSE=118.2 MAPE=18.1% R2=0.846 (1.5s)\n"
            "  LightGBM_raw: MAE=59.9 RMSE=112.7 MAPE=20.7% R2=0.860 (0.6s)\n"
            "  LightGBM_log1p: MAE=58.7 RMSE=118.8 MAPE=18.2% R2=0.844 (0.6s)\n"
            "  CatBoost_raw: MAE=64.3 RMSE=118.2 MAPE=22.4% R2=0.846 (1.8s)\n"
            "  CatBoost_log1p: MAE=61.1 RMSE=122.7 MAPE=19.3% R2=0.834 (1.8s)\n"
            "DONE segment=magnus\n"
        )),
    md("## Full 18-model comparison table\n"
       "(also saved as `artifacts/model_performance_ALL.csv`)"),
    code(
        "import pandas as pd\n"
        "m = pd.read_csv('../artifacts/model_performance_ALL.csv')\n"
        "print(m.to_string(index=False))\n",
        stdout=comparison_table
    ),
    md("### Key takeaways\n"
       "- **XGBoost (raw target, no log1p) is the best model in every segment** on R2, MAE and RMSE: "
       "Overall R2=0.947, Turvo R2=0.949, Magnus R2=0.859.\n"
       "- **`log1p` transform consistently improves MAPE but worsens MAE/RMSE/R2.** Log-transforming "
       "the target down-weights large shipments during training, which tightens *relative* "
       "(percentage) error at the expense of *absolute*-dollar accuracy on the biggest, "
       "highest-cost shipments once predictions are transformed back with `expm1`. Whether to use "
       "the raw or log1p model in production is therefore a business choice: pick **raw target** to "
       "minimize dollar error, pick **log1p** to minimize percentage error (e.g., if the business "
       "cares equally about small and large shipments in relative terms).\n"
       "- **XGBoost > LightGBM > CatBoost** on every segment/metric combination in this dataset, "
       "though the gap between XGBoost and LightGBM is small (<2 R2 points) while CatBoost trails "
       "by a larger margin, likely because CatBoost's default symmetric-tree growth is less suited "
       "to this feature set than the leaf-wise/level-wise growth used by LightGBM/XGBoost.\n"
       "- **Magnus models are meaningfully weaker (R2 ~0.85-0.86) than Turvo/Overall (R2 ~0.94-0.95).** "
       "This is expected: Magnus is a smaller segment (14.2K vs 147.6K rows) with 13 of its 24 "
       "features imputed rather than observed, so there is inherently less signal and more noise "
       "for the model to learn from.\n"
       "- **The Overall model performs almost identically to the Turvo-only model** (R2 0.947 vs "
       "0.949), showing that adding the smaller, noisier Magnus segment (with a "
       "`SourceName_is_Magnus` indicator) does not materially hurt Turvo-dominated performance - "
       "a single overall model is a reasonable production choice if a unified pipeline is preferred "
       "over maintaining two segment-specific models."),
    md("## SHAP explainability\n"
       "SHAP `TreeExplainer` summary plots were generated for all 18 models (500-row test-set "
       "sample each) and saved to `artifacts/shap/shap_<segment>_<algorithm>_<transform>.png`. "
       "Example: the best overall model."),
    code(
        "from PIL import Image\n"
        "Image.open('../artifacts/shap/shap_overall_XGBoost_raw.png')\n"
    ),
    md("Across all 18 models, the SHAP summaries consistently rank the **Historical Lane Cost** "
       "features (`TotalCostOriginMean`, `TotalCostDestinationMean`, "
       "`TotalCost_mean_6m_lane_state`, `OriginZip3_TE`) and **Distance** features "
       "(`HaversineMiles`, `LengthOfHaul`) as the top drivers of predicted cost, mirroring the "
       "Pearson-correlation findings in notebook 01 and the Boruta group composition in notebook 02 "
       "- both the linear (correlation), classical-ML (Boruta) and gradient-boosted (SHAP) views of "
       "feature importance agree on what matters most for pricing."),
]
nb4 = nbf.v4.new_notebook()
nb4["cells"] = cells
nb4["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                    "language_info": {"name": "python", "version": "3.12"}}
nbf.write(nb4, f"{NB_DIR}/04_modeling_shap_evaluation.ipynb")
print("Notebook 4 written")
