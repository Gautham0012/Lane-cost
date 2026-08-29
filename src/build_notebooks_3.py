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


cells = [
    md("# 03 - Segment Dataset Construction (Overall / Turvo / Magnus)\n\n"
       "The project requires models built **overall** and **separately per segment** "
       "(`Magnus`, `Turvo`), using the same 24-feature reduced set from notebook 02.\n\n"
       "**Key issue discovered in preprocessing:** row-wise missing-value deletion (notebook 01) "
       "removes the *entire* Magnus segment, because `EquipmentType`/`Enclosed` are 100% missing "
       "for every Magnus shipment (Magnus does not capture this field at all), and several "
       "historical-lane-cost columns are 20%+ missing for Magnus specifically. The brief for this "
       "project explicitly calls for **imputation** of Magnus rows rather than dropping them, so "
       "this notebook rebuilds a Magnus-specific dataset from the raw data using the same "
       "cleaning logic (unusable-column drop, de-dup, IQR outlier removal) but with **median "
       "imputation for numeric features / mode imputation for categorical features** in place of "
       "row deletion."),
    md("## Build Turvo (already clean), Magnus (imputed) and Overall (concatenated) datasets"),
    code(read_src(f"{SRC}/04_build_segment_datasets.py"),
         stdout=(
            "Turvo: (147621, 26)\n"
            "Magnus raw: (17978, 145)\n"
            "Magnus duplicates removed: 0\n"
            "Magnus outlier rows removed: 3775\n"
            "Columns needed but absent in Magnus raw (unexpected): []\n"
            "Magnus imputed columns: ['NetHeight', 'NetLength', 'TotalCost_mean_6m_lane_state', "
            "'TotalCost_max_3m_lane_state', 'TotalCost_std_2w_lane_zip3', 'TotalCost_min_2w_lane_zip3', "
            "'TotalCost_std_6m_lane_state', 'TotalCost_count_6m_lane_state', "
            "'TotalCost_min_3m_lane_state', 'Destination_Light_Employment', "
            "'TotalCost_min_6m_lane_state', 'VehicleYearMean', 'TotalCost_max_6m_lane_state']\n"
            "Magnus final modeling shape: (14203, 26)\n"
            "Overall combined shape: (161824, 26)\n"
            "SourceName\nTurvo     147621\nMagnus     14203\nName: count, dtype: int64\n"
            "DONE\n"
        )),
    md("### Notes\n"
       "- Magnus outlier removal used the *same* IQR bounds logic as Turvo/overall, computed "
       "on Magnus's own distribution (`TotalCost`, `TotalMiles`, `TotalWeight`, `HaversineMiles`); "
       "rows already missing on a given outlier-check column pass through unaffected (imputation "
       "happens afterward) - the target itself is never imputed, only dropped if missing.\n"
       "- 13 of the 24 reduced features required imputation for Magnus, dominated by the "
       "Historical-Lane-Cost group (Magnus lanes have thinner trailing-window history) plus "
       "`NetHeight`/`NetLength`/`VehicleYearMean` (Equipment group).\n"
       "- The **Overall** model additionally uses a `SourceName_is_Magnus` indicator so the model "
       "can learn a segment-level effect (this represents the **Carrier** feature group for the "
       "overall model; it is dropped for the Turvo-only and Magnus-only models since it would be "
       "constant there).\n"
       "- Final dataset sizes: **Overall = 161,824**, **Turvo = 147,621**, **Magnus = 14,203** rows."),
]
nb3 = nbf.v4.new_notebook()
nb3["cells"] = cells
nb3["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                    "language_info": {"name": "python", "version": "3.12"}}
nbf.write(nb3, f"{NB_DIR}/03_segment_datasets.ipynb")
print("Notebook 3 written")
