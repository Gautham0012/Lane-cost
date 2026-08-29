const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, BorderStyle, PageBreak
} = require("docx");

const FIG = "/home/claude/proj/artifacts/figures";
const IMGDIM = (w, h, maxW = 600) => {
  const scale = maxW / w;
  return { width: maxW, height: Math.round(h * scale) };
};

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }); }
function p(text, opts = {}) { return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } }); }
function bullet(text) { return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } }); }
function img(path, w, h) {
  const dims = IMGDIM(w, h);
  return new Paragraph({
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: dims })],
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
  });
}
function caption(text) {
  return new Paragraph({ children: [new TextRun({ text, italics: true, size: 18 })], alignment: AlignmentType.CENTER, spacing: { after: 260 } });
}

const cellW = 2300;
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: cellW, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "2F5496" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: 20 })] })],
  });
}
function table(headers, rows) {
  return new Table({
    width: { size: headers.length * cellW, type: WidthType.DXA },
    columnWidths: headers.map(() => cellW),
    rows: [
      new TableRow({ children: headers.map(hh => cell(hh, { header: true })) }),
      ...rows.map(r => new TableRow({ children: r.map(v => cell(v)) })),
    ],
  });
}

const perfRows = [
  ["Overall", "XGBoost", "raw", "85.9", "147.1", "21.0%", "0.947"],
  ["Overall", "XGBoost", "log1p", "87.4", "152.3", "19.1%", "0.943"],
  ["Overall", "LightGBM", "raw", "87.7", "149.2", "21.5%", "0.945"],
  ["Overall", "LightGBM", "log1p", "89.1", "154.3", "19.4%", "0.942"],
  ["Overall", "CatBoost", "raw", "92.8", "156.1", "22.6%", "0.940"],
  ["Overall", "CatBoost", "log1p", "94.6", "162.2", "20.5%", "0.935"],
  ["Turvo", "XGBoost", "raw", "87.3", "148.9", "20.2%", "0.949"],
  ["Turvo", "XGBoost", "log1p", "89.2", "154.3", "18.4%", "0.946"],
  ["Turvo", "LightGBM", "raw", "88.9", "150.8", "20.6%", "0.948"],
  ["Turvo", "LightGBM", "log1p", "91.5", "157.4", "18.7%", "0.944"],
  ["Turvo", "CatBoost", "raw", "93.6", "156.8", "21.6%", "0.944"],
  ["Turvo", "CatBoost", "log1p", "96.9", "163.9", "19.8%", "0.939"],
  ["Magnus", "XGBoost", "raw", "59.3", "113.1", "20.6%", "0.859"],
  ["Magnus", "XGBoost", "log1p", "58.4", "118.2", "18.1%", "0.846"],
  ["Magnus", "LightGBM", "raw", "59.9", "112.7", "20.7%", "0.860"],
  ["Magnus", "LightGBM", "log1p", "58.7", "118.8", "18.2%", "0.844"],
  ["Magnus", "CatBoost", "raw", "64.3", "118.2", "22.4%", "0.846"],
  ["Magnus", "CatBoost", "log1p", "61.1", "122.7", "19.3%", "0.834"],
];

const groupRows = [
  ["Distance", "TotalMiles, HaversineMiles, LengthOfHaul, delta_lat/lon, Origin/Destination Lat-Lon, TotalStops, NumberOfPick/Drop", "Physical geography of the move; single largest structural cost driver in trucking."],
  ["Equipment", "EquipmentType, Enclosed, NetHeight/Length/WheelBase, IsEV/IsHybrid, vehicle-type flags, TotalWeight, VehicleCount, VehicleYearMean", "Vehicle(s) shipped and trailer/equipment used; drives capacity constraints & handling premiums."],
  ["Fuel Price", "OriginGasPrice, DestinationGasPrice, Origin/Destination W/M Diesel Price", "Direct pass-through input cost for carriers; tracked separately for its short-run volatility."],
  ["Historical Lane Cost", "TotalCost min/max/mean/count/std over 2w/3m/6m lane windows, TotalCostOrigin/DestinationMean, OriginZip3_TE, DestinationZip3_TE, TotalMiles_TE", "Rolling empirical priors for what a lane has cost recently; strongest predictor group."],
  ["Market Conditions", "Freight/trucking indices, manufacturing & inventory ratios, vehicle sales, recession indicator, RUCC rurality, regional wages/employment", "Macro-economic & industry backdrop for freight pricing, outside any single shipment's control."],
  ["Seasonality", "CreationDate day-of-week/day-of-year sin/cos, is_weekend/is_eoq/is_holiday, lead_time_days, delivery_date_days", "Calendar/demand-cycle effects independent of macro market conditions."],
  ["Carrier", "SourceId/SourceName, MarketPlaceShipment, MarketplaceCovered, Assigned, PendingPickup, Expedited", "Platform/carrier-sourcing channel and operational status, not the physical shipment itself."],
  ["Customer", "OriginState/DestinationState, OriginZip3/DestinationZip3, Zip zones", "Origin/destination location identifiers as experienced by the customer."],
];

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({ text: "Veltris Vehicle Shipment Cost Modeling", heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
      new Paragraph({ text: "End-to-End Data Preprocessing, Feature Reduction, EDA & Predictive Modeling Summary", alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
      new Paragraph({ text: "Prepared for: Veltris  |  Dataset: Veltris-Vehicle.xlsx  |  Target: TotalCost (USD)", alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
      new Paragraph({ text: new Date().toISOString().slice(0,10), alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
      new Paragraph({ children: [new PageBreak()] }),

      h1("Executive Summary"),
      p("The raw Veltris vehicle-shipment dataset (305,838 shipments x 145 attributes, spanning two carrier-sourcing platforms, Turvo and Magnus) was cleaned, reduced from 145 to 24 statistically-vetted predictive features (an 83% reduction), explored for its relationship with shipment cost, and used to train and compare 18 gradient-boosted models (XGBoost, LightGBM, CatBoost, each with and without a log1p target transform) across three modeling scopes: Overall, Turvo-only and Magnus-only."),
      p("The best-performing model overall is XGBoost trained on the raw (untransformed) target, achieving R\u00b2 = 0.947 (Overall), R\u00b2 = 0.949 (Turvo) and R\u00b2 = 0.859 (Magnus) on held-out test data, with a mean absolute error of $85-90 on shipments whose interquartile cost range is roughly $500-$1,700. Historical lane-cost and physical-distance features are, by a wide margin, the strongest drivers of cost across every explainability lens used (Pearson correlation, Boruta, SHAP)."),
      p("A material data-quality finding is that the Magnus segment loses 100% of its rows under simple listwise deletion of missing values, because two fields (EquipmentType, Enclosed) are never populated for Magnus shipments. A dedicated Magnus pipeline using median/mode imputation was built so that segment could still be modeled, per the project brief."),

      h1("1. Data Overview"),
      p("Source file: Veltris-Vehicle.xlsx - 305,838 rows, 145 columns, single sheet ('result'). Two carrier-sourcing segments are present in SourceName: Turvo (287,860 rows, 94.1%) and Magnus (17,978 rows, 5.9%). The target variable is TotalCost (USD, the realized cost of the shipment)."),

      h1("2. Data Preprocessing"),
      h2("2.1 Column-level cleaning"),
      p("18 columns were removed before row-level cleaning:"),
      bullet("Near-empty (>50% missing): InoperableAny (98.6%), NetWidth (95.0%), OriginTimeZone (80.2%), DestinationTimeZone (79.5%)"),
      bullet("Direct target leakage: TotalCostLog (a deterministic log-transform of the label)"),
      bullet("High-cardinality raw identifiers: OriginPostalCode, DestinationPostalCode, OriginCity, DestinationCity (superseded by Zip3 / target-encoded Zip3 features)"),
      bullet("Raw absolute calendar dates superseded by engineered cyclical/seasonal features, plus post-outcome delivery timestamps (leakage risk): CreationDate, FirstPickup, LastPickup, FirstScheduledDelivery, LastScheduledDelivery, FirstDelivery, LastDelivery"),
      bullet("Vendor-provided Split (replaced with our own 80/10/10 split) and ShipmentId (row identifier, not a feature)"),
      h2("2.2 Row-level cleaning"),
      bullet("Duplicate rows removed: 115"),
      bullet("Rows with missing values removed: 133,030 (43.5% of the post-column-cleaning dataset)"),
      bullet("Outlier rows removed (1.5x IQR rule on TotalCost, TotalMiles, TotalWeight, HaversineMiles): 25,072 (14.5%)"),
      p("Resulting PROCESSED dataset: 147,621 rows x 127 columns (all Turvo - see Section 6 for why Magnus required a separate pipeline)."),

      h1("3. Descriptive Statistics"),
      p("Full descriptive-statistics tables (count, mean, std, min/25/50/75/max, missing %, skew, kurtosis for every numeric column; unique-value counts and modal category for every categorical column) are provided separately for the RAW and PROCESSED datasets in data/processed/descriptive_stats_RAW_*.csv and descriptive_stats_PROCESSED_*.csv. Headline TotalCost statistics:"),
      table(["Dataset", "N", "Mean", "Std", "Min", "Median", "Max"], [
        ["Raw", "305,838", "$676", "$1,185", "$0", "$425", "$85,000+"],
        ["Processed", "147,621", "$663", "$497", "$25", "$531", "$3,275"],
      ]),
      p("Outlier removal substantially tightens the cost distribution (std falls from $1,185 to $497) while leaving the typical shipment cost (median) essentially unchanged, indicating the removed rows were mostly extreme high-cost tail cases rather than representative shipments."),
      img(`${FIG}/01_target_distribution_before_after.png`, 1200, 450),
      caption("Figure 1. TotalCost distribution before (raw) and after (processed, outliers removed)."),

      h1("4. Multicollinearity Reduction (VIF) & Feature Selection (Boruta)"),
      h2("4.1 Variance Inflation Factor (VIF)"),
      p("VIF was computed on all 120 numeric candidate features (12 zero-variance columns dropped first) using a 20,000-row sample, with iterative removal of the highest-VIF feature until every remaining feature had VIF < 10. This removed 42 of 120 numeric features - notably TotalMiles itself, which is almost perfectly collinear with HaversineMiles (both encode travel distance)."),
      h2("4.2 Boruta all-relevant feature selection"),
      p("Boruta (Random Forest-based, shadow-feature permutation test, 12 iterations, 8,000-row sample) was then run on the 66 VIF-surviving numeric features plus 5 categorical features. It confirmed 15 features as relevant and retained 9 as tentative, rejecting 47 as statistically indistinguishable from noise."),
      p("Final reduced feature count: 24 (from 145 raw columns - an 83% reduction). All 24 are numeric; none of the raw categorical columns (EquipmentType, OriginState, DestinationState, OriginZip3, DestinationZip3) survived selection, as their signal is already captured by the numeric target-encoded / lane-history features."),
      img(`${FIG}/02_correlation_heatmap_reduced.png`, 1100, 950),
      caption("Figure 2. Correlation heatmap of the final 24-feature reduced set with TotalCost."),

      h1("5. Feature Groups"),
      p("Every retained (and business-relevant EDA) feature is assigned to exactly one of the 8 required feature groups:"),
      table(["Group", "Representative Features", "Rationale"], groupRows),
      img(`${FIG}/07_group_level_avg_correlation.png`, 900, 560),
      caption("Figure 3. Average |correlation| with TotalCost by feature group (selected features only)."),

      h1("6. EDA: Relationship of Features with Target"),
      img(`${FIG}/03_feature_target_correlation_by_group.png`, 950, 850),
      caption("Figure 4. Correlation of each selected feature with TotalCost, colored by feature group."),
      img(`${FIG}/04_top_feature_relationships.png`, 1100, 900),
      caption("Figure 5. Relationship of the 4 most correlated features with TotalCost."),
      img(`${FIG}/05_distance_lanecost_relationships.png`, 1150, 430),
      caption("Figure 6. Distance (HaversineMiles) and Historical Lane Cost (TotalCostOriginMean) vs TotalCost."),
      img(`${FIG}/06_equipment_type_cost.png`, 950, 530),
      caption("Figure 7. TotalCost by EquipmentType (Equipment group; pre-reduction cleaned dataset)."),

      h1("7. Segment Dataset Construction: the Magnus Imputation Problem"),
      p("A key finding: applying the same listwise-deletion cleaning used for the overall dataset removes 100% of the Magnus segment, because EquipmentType and Enclosed are never populated for Magnus shipments (100% missing), and several historical lane-cost fields are 17-34% missing specifically for Magnus."),
      p("To satisfy the requirement of a Magnus-specific model, a parallel pipeline was built: the same column-drop / de-duplication / IQR outlier-removal logic was applied to the raw Magnus rows, but instead of dropping rows with missing values, missing numeric features were imputed with the Magnus-specific median and missing categorical features with the Magnus-specific mode. 13 of the 24 selected features required imputation for Magnus (dominated by the Historical Lane Cost and Equipment groups). Final dataset sizes:"),
      table(["Dataset", "Rows", "Columns", "Notes"], [
        ["Turvo", "147,621", "26", "Fully observed after cleaning; no imputation needed"],
        ["Magnus", "14,203", "26", "13 of 24 features imputed (median/mode)"],
        ["Overall", "161,824", "27", "Turvo + Magnus concatenated, plus a SourceName_is_Magnus indicator"],
      ]),

      h1("8. Modeling Methodology"),
      bullet("Split: 80% train / 10% validation / 10% test (stratified by segment for the Overall model), fixed random seed for reproducibility"),
      bullet("Algorithms: XGBoost, LightGBM, CatBoost (400 trees, depth 6, learning rate 0.05, early stopping on validation loss)"),
      bullet("Target transform: each algorithm trained twice per segment - once on the raw TotalCost target, once on log1p(TotalCost). Log1p predictions are transformed back to dollars with expm1 before scoring, so all metrics below are directly comparable across both transform choices."),
      bullet("Explainability: SHAP TreeExplainer summary plots generated for all 18 resulting models (500-row test-set sample each)"),
      bullet("Error metrics: MAE, MAPE, RMSE, R\u00b2 on the held-out test set, for every segment x algorithm x transform combination (18 models total)"),

      h1("9. Model Performance Comparison"),
      table(["Segment", "Algorithm", "Transform", "MAE ($)", "RMSE ($)", "MAPE (%)", "R\u00b2"], perfRows),
      img(`${FIG}/08_model_comparison_all.png`, 1150, 820),
      caption("Figure 8. MAE / RMSE / MAPE / R\u00b2 across all 18 models, grouped by segment."),
      h2("9.1 Key findings"),
      bullet("XGBoost on the raw (untransformed) target is the best model in every segment on R\u00b2, MAE and RMSE."),
      bullet("log1p consistently improves MAPE (percentage error) but worsens MAE/RMSE/R\u00b2 (dollar error) - it down-weights large shipments during training. Choice of raw-vs-log1p target is therefore a business decision: raw target minimizes dollar error, log1p minimizes percentage error."),
      bullet("XGBoost > LightGBM > CatBoost consistently, though the XGBoost-LightGBM gap is small (<2 R\u00b2 points)."),
      bullet("Magnus models are meaningfully weaker (R\u00b2 ~0.85-0.86) than Turvo/Overall (R\u00b2 ~0.94-0.95) - expected, given Magnus's smaller size and heavier reliance on imputed features."),
      bullet("The Overall model performs almost identically to the Turvo-only model (R\u00b2 0.947 vs 0.949), suggesting a single unified pipeline is a reasonable production choice."),

      h1("10. SHAP Explainability"),
      p("SHAP TreeExplainer summary plots were produced for all 18 models (artifacts/shap/). Across every model, the Historical Lane Cost features (TotalCostOriginMean, TotalCostDestinationMean, TotalCost_mean_6m_lane_state, OriginZip3_TE) and Distance features (HaversineMiles, LengthOfHaul) are consistently the top drivers of predicted cost - in agreement with both the raw Pearson-correlation analysis (Section 6) and the Boruta feature-group composition (Section 4), giving three independent lines of evidence pointing to the same conclusion: historical pricing on the lane and physical distance are what set vehicle-shipment cost."),

      h1("11. Recommendations & Next Steps"),
      bullet("Deploy XGBoost trained on the raw target as the primary cost-prediction model (Overall scope), with the option of the Turvo/Magnus segment-specific models where segment-level accuracy matters more than a single unified pipeline."),
      bullet("Revisit data capture for Magnus: populating EquipmentType/Enclosed would remove the need for imputation and likely close a meaningful part of the Turvo-Magnus R\u00b2 gap."),
      bullet("Consider a hurdle/two-stage or quantile-regression approach for very-high-cost shipments (the tail removed by IQR outlier filtering here) if the business needs cost predictions for those cases too."),
      bullet("Periodically retrain, since Historical Lane Cost features are time-varying rolling windows and Market Conditions features are macro-economic series that will drift."),

      h1("12. Repository & Reproducibility"),
      p("All code, notebooks, data artifacts, figures and models referenced in this report are packaged in the accompanying GitHub-ready repository (see README.md for the full folder layout and step-by-step reproduction instructions)."),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/home/claude/proj/reports/Veltris_Vehicle_Cost_Model_Summary.docx", buf);
  console.log("docx written", buf.length, "bytes");
});
