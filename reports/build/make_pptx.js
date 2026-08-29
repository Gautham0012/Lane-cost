const pptxgen = require("pptxgenjs");
const path = require("path");

const FIG = "/home/claude/proj/artifacts/figures";
const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const SLATE = "3A3F5C";
const GOLD = "D6A419";
const DARKTXT = "1B1F30";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };

function titleBar(slide, title, subtitle) {
  slide.addText(title, { x: 0.5, y: 0.35, w: 12.3, h: 0.7, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, isTextBox: true });
  if (subtitle) {
    slide.addText(subtitle, { x: 0.5, y: 0.95, w: 12.3, h: 0.4, fontFace: "Calibri", fontSize: 14, color: SLATE, isTextBox: true });
  }
}
function pageNum(slide, n) {
  slide.addText(String(n), { x: 12.7, y: 7.1, w: 0.5, h: 0.3, fontSize: 10, color: "9A9A9A", align: "right", isTextBox: true });
}

// ---------------------------------------------------------------- Slide 1: Title
{
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 4.55, w: 13.33, h: 2.95, fill: { color: "17204F" }, line: { type: "none" } });
  s.addText("Veltris Vehicle Shipment\nCost Modeling", {
    x: 0.9, y: 2.15, w: 11.5, h: 2.0, fontFace: "Cambria", fontSize: 44, bold: true, color: WHITE, isTextBox: true,
  });
  s.addText("Data Preprocessing \u2022 Feature Reduction \u2022 EDA \u2022 Predictive Modeling", {
    x: 0.9, y: 4.75, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 18, color: ICE, isTextBox: true,
  });
  s.addText("Dataset: Veltris-Vehicle.xlsx  |  Target: TotalCost (USD)  |  " + new Date().toISOString().slice(0, 10), {
    x: 0.9, y: 5.35, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "9FB3E8", isTextBox: true,
  });
}

// ---------------------------------------------------------------- Slide 2: Executive summary (stat callouts)
{
  let s = pres.addSlide();
  titleBar(s, "Executive Summary", "305,838 raw shipments \u2192 24 predictive features \u2192 18 models compared");
  const stats = [
    { n: "83%", l: "dimensionality reduction\n(145 \u2192 24 features)" },
    { n: "0.947", l: "best test R\u00b2\n(Overall, XGBoost)" },
    { n: "$86", l: "MAE on Overall model\n(XGBoost, raw target)" },
    { n: "18", l: "models trained & SHAP-explained\n(3 algorithms x 2 transforms x 3 segments)" },
  ];
  const boxW = 2.85, gap = 0.28, startX = 0.6;
  stats.forEach((st, i) => {
    const x = startX + i * (boxW + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.65, w: boxW, h: 1.9, rectRadius: 0.08, fill: { color: "F3F5FC" }, line: { color: ICE, width: 1 } });
    s.addText(st.n, { x, y: 1.8, w: boxW, h: 0.85, align: "center", fontFace: "Cambria", fontSize: 36, bold: true, color: NAVY, isTextBox: true });
    s.addText(st.l, { x: x + 0.1, y: 2.65, w: boxW - 0.2, h: 0.8, align: "center", fontFace: "Calibri", fontSize: 11.5, color: SLATE, isTextBox: true });
  });
  s.addText(
    [
      { text: "The best model (XGBoost, raw target) explains 94.7% of cost variance overall and 94.9% for the Turvo segment. ", options: {} },
      { text: "Historical lane cost and physical distance are the strongest, most consistent drivers of cost across correlation, Boruta and SHAP analysis. ", options: {} },
      { text: "A key data-quality finding \u2014 the entire Magnus segment is lost under simple missing-value deletion \u2014 was solved with a dedicated imputation pipeline.", options: {} },
    ],
    { x: 0.6, y: 4.0, w: 12.1, h: 1.9, fontFace: "Calibri", fontSize: 15, color: DARKTXT, valign: "top", isTextBox: true, lineSpacingMultiple: 1.25 }
  );
  pageNum(s, 2);
}

// ---------------------------------------------------------------- Slide 3: Data overview
{
  let s = pres.addSlide();
  titleBar(s, "Data Overview", "One raw file, two carrier-sourcing segments");
  s.addTable(
    [
      [{ text: "Attribute", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "Value", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
      ["Source file", "Veltris-Vehicle.xlsx (single sheet 'result')"],
      ["Raw rows / columns", "305,838 rows x 145 columns"],
      ["Target variable", "TotalCost (USD)"],
      ["Segments (SourceName)", "Turvo: 287,860 rows (94.1%)   |   Magnus: 17,978 rows (5.9%)"],
      ["Feature domains present", "Distance, Equipment, Fuel Price, Historical Lane Cost, Market\nConditions, Seasonality, Carrier, Customer"],
    ],
    { x: 0.6, y: 1.7, w: 9.4, colW: [3.2, 6.2], fontSize: 13, fontFace: "Calibri", border: { type: "solid", color: "D9DEEC", pt: 0.75 }, autoPage: false, rowH: 0.55 }
  );
  s.addShape(pres.ShapeType.roundRect, { x: 10.25, y: 1.7, w: 2.5, h: 4.0, rectRadius: 0.08, fill: { color: "F3F5FC" }, line: { color: ICE, width: 1 } });
  s.addText("94.1%", { x: 10.25, y: 2.0, w: 2.5, h: 0.7, align: "center", fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, isTextBox: true });
  s.addText("Turvo share\nof shipments", { x: 10.35, y: 2.65, w: 2.3, h: 0.6, align: "center", fontSize: 11, color: SLATE, isTextBox: true });
  s.addText("5.9%", { x: 10.25, y: 3.5, w: 2.5, h: 0.7, align: "center", fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, isTextBox: true });
  s.addText("Magnus share\nof shipments", { x: 10.35, y: 4.15, w: 2.3, h: 0.6, align: "center", fontSize: 11, color: SLATE, isTextBox: true });
  s.addText("145", { x: 10.25, y: 5.0, w: 2.5, h: 0.7, align: "center", fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, isTextBox: true });
  s.addText("raw attributes\nper shipment", { x: 10.35, y: 5.65, w: 2.3, h: 0.6, align: "center", fontSize: 11, color: SLATE, isTextBox: true });
  pageNum(s, 3);
}

// ---------------------------------------------------------------- Slide 4: Preprocessing pipeline
{
  let s = pres.addSlide();
  titleBar(s, "Data Preprocessing Pipeline", "305,838 \u2192 147,621 clean rows (Turvo); Magnus handled separately (see slide 9)");
  const steps = [
    ["1. Drop unusable columns", "18 columns removed: >50% missing, target leakage,\nhigh-cardinality IDs, redundant raw dates"],
    ["2. Remove duplicates", "115 exact-duplicate rows removed"],
    ["3. Remove missing rows", "133,030 rows (43.5%) dropped for missing values\nin the retained columns"],
    ["4. Remove outliers", "25,072 rows (14.5%) removed via 1.5x IQR rule on\nTotalCost, TotalMiles, TotalWeight, HaversineMiles"],
  ];
  const colW = 2.95, gap = 0.15, startX = 0.5;
  steps.forEach((st, i) => {
    const x = startX + i * (colW + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.75, w: colW, h: 2.5, rectRadius: 0.08, fill: { color: i % 2 === 0 ? "F3F5FC" : "EAEFFA" }, line: { color: ICE, width: 1 } });
    s.addText(st[0], { x: x + 0.15, y: 1.9, w: colW - 0.3, h: 0.6, fontFace: "Cambria", fontSize: 14.5, bold: true, color: NAVY, isTextBox: true });
    s.addText(st[1], { x: x + 0.15, y: 2.55, w: colW - 0.3, h: 1.6, fontFace: "Calibri", fontSize: 11.5, color: DARKTXT, isTextBox: true, valign: "top" });
    if (i < 3) s.addText("\u2192", { x: x + colW - 0.05, y: 2.7, w: 0.3, h: 0.5, fontSize: 20, bold: true, color: GOLD, align: "center", isTextBox: true });
  });
  s.addText("Result: 147,621 rows x 127 columns (fully-observed, outlier-trimmed Turvo dataset)", {
    x: 0.5, y: 4.6, w: 12.3, h: 0.5, fontFace: "Calibri", fontSize: 15, italic: true, color: SLATE, isTextBox: true,
  });
  s.addImage({ path: `${FIG}/01_target_distribution_before_after.png`, x: 0.9, y: 5.15, w: 11.3, h: 1.95 });
  pageNum(s, 4);
}

// ---------------------------------------------------------------- Slide 5: VIF + Boruta
{
  let s = pres.addSlide();
  titleBar(s, "Multicollinearity Reduction & Feature Selection", "VIF (statistical redundancy) + Boruta (all-relevant importance)");
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.75, w: 5.9, h: 4.9, rectRadius: 0.08, fill: { color: "F3F5FC" }, line: { color: ICE, width: 1 } });
  s.addText("Step 1 \u2014 VIF elimination", { x: 0.75, y: 1.95, w: 5.4, h: 0.5, fontFace: "Cambria", fontSize: 18, bold: true, color: NAVY, isTextBox: true });
  s.addText(
    [
      { text: "120 numeric candidates (12 zero-variance columns dropped first)", options: { bullet: true, breakLine: true } },
      { text: "Iteratively remove the highest-VIF feature until all VIF < 10", options: { bullet: true, breakLine: true } },
      { text: "42 features removed \u2014 including TotalMiles itself (near-perfect collinearity with HaversineMiles)", options: { bullet: true, breakLine: true } },
      { text: "66 numeric features survive", options: { bullet: true, breakLine: false } },
    ],
    { x: 0.85, y: 2.55, w: 5.2, h: 3.9, fontFace: "Calibri", fontSize: 13.5, color: DARKTXT, isTextBox: true, valign: "top", paraSpaceAfter: 14, lineSpacingMultiple: 1.15 }
  );
  s.addShape(pres.ShapeType.roundRect, { x: 6.6, y: 1.75, w: 5.9, h: 4.9, rectRadius: 0.08, fill: { color: "F3F5FC" }, line: { color: ICE, width: 1 } });
  s.addText("Step 2 \u2014 Boruta selection", { x: 6.85, y: 1.95, w: 5.4, h: 0.5, fontFace: "Cambria", fontSize: 18, bold: true, color: NAVY, isTextBox: true });
  s.addText(
    [
      { text: "Random-Forest shadow-feature test on the 66 VIF survivors + 5 categorical features (71 candidates)", options: { bullet: true, breakLine: true } },
      { text: "15 features Confirmed, 9 Tentative (kept), 47 Rejected as noise", options: { bullet: true, breakLine: true } },
      { text: "Final reduced feature count: 24 \u2014 all numeric", options: { bullet: true, breakLine: true } },
      { text: "83% reduction from the original 145 raw columns", options: { bullet: true, breakLine: false } },
    ],
    { x: 6.95, y: 2.55, w: 5.2, h: 3.9, fontFace: "Calibri", fontSize: 13.5, color: DARKTXT, isTextBox: true, valign: "top", paraSpaceAfter: 14, lineSpacingMultiple: 1.15 }
  );
  pageNum(s, 5);
}

// ---------------------------------------------------------------- Slide 6: Feature groups
{
  let s = pres.addSlide();
  titleBar(s, "Feature Groups", "Every selected feature mapped to one of 8 business-meaningful groups");
  const groups = [
    ["Distance", "5 features", "Physical geography of the move"],
    ["Historical Lane Cost", "12 features", "What this lane has cost recently"],
    ["Equipment", "4 features", "Vehicle & trailer specifications"],
    ["Market Conditions", "3 features", "Macro & regional labor backdrop"],
    ["Fuel Price", "0 selected*", "Gas/diesel pass-through cost"],
    ["Seasonality", "0 selected*", "Calendar & demand-cycle effects"],
    ["Carrier", "0 selected*", "Sourcing channel & operational flags"],
    ["Customer", "0 selected*", "Origin/destination geography (categorical)"],
  ];
  const colW = 2.95, rowH = 1.55, gapX = 0.15, gapY = 0.2, startX = 0.5, startY = 1.75;
  groups.forEach((g, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = startX + col * (colW + gapX), y = startY + row * (rowH + gapY);
    const dim = g[1].includes("0 selected");
    s.addShape(pres.ShapeType.roundRect, { x, y, w: colW, h: rowH, rectRadius: 0.08, fill: { color: dim ? "F3F3F5" : "EAEFFA" }, line: { color: dim ? "E2E2E6" : ICE, width: 1 } });
    s.addText(g[0], { x: x + 0.15, y: y + 0.1, w: colW - 0.3, h: 0.4, fontFace: "Cambria", fontSize: 14, bold: true, color: dim ? "8A8A93" : NAVY, isTextBox: true });
    s.addText(g[1], { x: x + 0.15, y: y + 0.48, w: colW - 0.3, h: 0.32, fontFace: "Calibri", fontSize: 12, bold: true, color: dim ? "8A8A93" : GOLD, isTextBox: true });
    s.addText(g[2], { x: x + 0.15, y: y + 0.85, w: colW - 0.3, h: 0.6, fontFace: "Calibri", fontSize: 10.5, color: dim ? "9A9AA0" : DARKTXT, isTextBox: true });
  });
  s.addText("*Not selected by Boruta on this dataset in isolation, once Distance & Historical Lane Cost are known \u2014 still reported in the full EDA and available for future iterations.", {
    x: 0.5, y: 5.75, w: 12.3, h: 0.55, fontFace: "Calibri", fontSize: 11, italic: true, color: SLATE, isTextBox: true,
  });
  pageNum(s, 6);
}

// ---------------------------------------------------------------- Slide 7: EDA - correlation
{
  let s = pres.addSlide();
  titleBar(s, "EDA: What Drives Shipment Cost", "Correlation of each selected feature with TotalCost, by feature group");
  s.addImage({ path: `${FIG}/03_feature_target_correlation_by_group.png`, x: 2.55, y: 1.55, w: 8.2, h: 5.55 });
  pageNum(s, 7);
}

// ---------------------------------------------------------------- Slide 8: EDA - top relationships
{
  let s = pres.addSlide();
  titleBar(s, "EDA: Top Feature Relationships", "Distance and lane-history features show the clearest relationship with cost");
  s.addImage({ path: `${FIG}/05_distance_lanecost_relationships.png`, x: 0.6, y: 1.7, w: 12.1, h: 4.5 });
  pageNum(s, 8);
}

// ---------------------------------------------------------------- Slide 9: Magnus imputation
{
  let s = pres.addSlide();
  titleBar(s, "The Magnus Imputation Problem", "A data-quality finding that required a dedicated segment pipeline");
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.7, w: 6.3, h: 4.9, rectRadius: 0.08, fill: { color: "FBF2E3" }, line: { color: "EAD9AE", width: 1 } });
  s.addText("\u26A0  Finding", { x: 0.75, y: 1.9, w: 5.8, h: 0.5, fontFace: "Cambria", fontSize: 17, bold: true, color: "8A5A00", isTextBox: true });
  s.addText(
    "Standard listwise deletion of missing values removes 100% of the Magnus segment. " +
    "EquipmentType and Enclosed are never populated for Magnus shipments (100% missing), and several " +
    "historical lane-cost fields are 17\u201334% missing specifically for Magnus.",
    { x: 0.85, y: 2.5, w: 5.7, h: 2.0, fontFace: "Calibri", fontSize: 14, color: DARKTXT, isTextBox: true, valign: "top" }
  );
  s.addText("\u2713  Solution", { x: 0.75, y: 4.55, w: 5.8, h: 0.5, fontFace: "Cambria", fontSize: 17, bold: true, color: "2C5F2D", isTextBox: true });
  s.addText(
    "A dedicated Magnus pipeline applies the same cleaning logic but IMPUTES missing values " +
    "(median for numeric, mode for categorical, fit on Magnus's own distribution) instead of dropping rows. " +
    "13 of 24 selected features required imputation.",
    { x: 0.85, y: 5.15, w: 5.7, h: 1.3, fontFace: "Calibri", fontSize: 13, color: DARKTXT, isTextBox: true, valign: "top" }
  );
  s.addTable(
    [
      [{ text: "Dataset", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "Rows", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "Notes", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
      ["Turvo", "147,621", "Fully observed; no imputation needed"],
      ["Magnus", "14,203", "13 of 24 features imputed"],
      ["Overall", "161,824", "Turvo + Magnus + segment indicator"],
    ],
    { x: 7.1, y: 1.9, w: 5.7, colW: [1.7, 1.3, 2.7], fontSize: 12.5, fontFace: "Calibri", border: { type: "solid", color: "D9DEEC", pt: 0.75 }, autoPage: false, rowH: 0.65 }
  );
  pageNum(s, 9);
}

// ---------------------------------------------------------------- Slide 10: Modeling methodology
{
  let s = pres.addSlide();
  titleBar(s, "Modeling Methodology", "18 models: 3 algorithms x 2 target transforms x 3 segments");
  const items = [
    ["Split", "80% train / 10% validation / 10% test, stratified by segment, fixed seed"],
    ["Algorithms", "XGBoost, LightGBM, CatBoost (400 trees, depth 6, lr 0.05, early stopping)"],
    ["Target transform", "Each algorithm trained on raw TotalCost AND log1p(TotalCost); log1p\npredictions transformed back with expm1 before scoring for fair comparison"],
    ["Explainability", "SHAP TreeExplainer summary plots for all 18 models (500-row test sample)"],
    ["Metrics", "MAE, MAPE, RMSE, R\u00b2 on held-out test data for every model"],
  ];
  let y = 1.75;
  items.forEach((it) => {
    s.addShape(pres.ShapeType.rect, { x: 0.6, y: y + 0.08, w: 0.09, h: 0.65, fill: { color: GOLD }, line: { type: "none" } });
    s.addText(it[0], { x: 0.9, y, w: 2.6, h: 0.8, fontFace: "Cambria", fontSize: 15, bold: true, color: NAVY, isTextBox: true, valign: "top" });
    s.addText(it[1], { x: 3.6, y, w: 9.1, h: 0.8, fontFace: "Calibri", fontSize: 13.5, color: DARKTXT, isTextBox: true, valign: "top" });
    y += 0.98;
  });
  pageNum(s, 10);
}

// ---------------------------------------------------------------- Slide 11: Model performance comparison
{
  let s = pres.addSlide();
  titleBar(s, "Model Performance Comparison", "XGBoost (raw target) is the best model in every segment");
  s.addTable(
    [
      [{ text: "Segment", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "Best Model", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "MAE", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "RMSE", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "MAPE", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
       { text: "R\u00b2", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
      ["Overall", "XGBoost (raw)", "$85.9", "$147.1", "21.0%", "0.947"],
      ["Turvo", "XGBoost (raw)", "$87.3", "$148.9", "20.2%", "0.949"],
      ["Magnus", "LightGBM (raw)", "$59.9", "$112.7", "20.7%", "0.860"],
    ],
    { x: 0.6, y: 1.7, w: 6.3, colW: [1.15, 1.85, 0.85, 0.9, 0.85, 0.7], fontSize: 12, fontFace: "Calibri", border: { type: "solid", color: "D9DEEC", pt: 0.75 }, autoPage: false, rowH: 0.5 }
  );
  s.addText("log1p transform: improves MAPE (\u22122pp avg) but worsens MAE/RMSE/R\u00b2 \u2014 a business trade-off between percentage and dollar accuracy.", {
    x: 0.6, y: 3.85, w: 6.3, h: 1.0, fontFace: "Calibri", fontSize: 12, italic: true, color: SLATE, isTextBox: true, valign: "top",
  });
  s.addText("XGBoost > LightGBM > CatBoost consistently, though the XGBoost\u2013LightGBM gap is small (<2 R\u00b2 points).", {
    x: 0.6, y: 4.85, w: 6.3, h: 0.8, fontFace: "Calibri", fontSize: 12, italic: true, color: SLATE, isTextBox: true, valign: "top",
  });
  s.addImage({ path: `${FIG}/08_model_comparison_all.png`, x: 7.1, y: 1.6, w: 5.7, h: 5.4 });
  pageNum(s, 11);
}

// ---------------------------------------------------------------- Slide 12: SHAP
{
  let s = pres.addSlide();
  titleBar(s, "SHAP Explainability", "Three independent methods agree: lane history & distance drive cost");
  s.addImage({ path: "/home/claude/proj/artifacts/shap/shap_overall_XGBoost_raw.png", x: 0.6, y: 1.55, w: 6.6, h: 5.3 });
  s.addText("Best overall model \u2014 SHAP summary", { x: 0.6, y: 6.85, w: 6.6, h: 0.35, align: "center", fontSize: 11, italic: true, color: SLATE, isTextBox: true });
  s.addShape(pres.ShapeType.roundRect, { x: 7.5, y: 1.7, w: 5.3, h: 4.9, rectRadius: 0.08, fill: { color: "F3F5FC" }, line: { color: ICE, width: 1 } });
  s.addText(
    [
      { text: "Historical Lane Cost features (TotalCostOriginMean, TotalCostDestinationMean, TotalCost_mean_6m_lane_state, OriginZip3_TE) are consistently the top SHAP drivers", options: { bullet: true, breakLine: true } },
      { text: "Distance features (HaversineMiles, LengthOfHaul) rank second across every one of the 18 models", options: { bullet: true, breakLine: true } },
      { text: "This agrees with the Pearson-correlation EDA (slide 7) and the Boruta group composition (slide 6) \u2014 three independent methods, one consistent answer", options: { bullet: true, breakLine: false } },
    ],
    { x: 7.75, y: 1.95, w: 4.8, h: 4.4, fontFace: "Calibri", fontSize: 13.5, color: DARKTXT, isTextBox: true, valign: "top", paraSpaceAfter: 14, lineSpacingMultiple: 1.15 }
  );
  pageNum(s, 12);
}

// ---------------------------------------------------------------- Slide 13: Recommendations
{
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Recommendations & Next Steps", { x: 0.7, y: 0.5, w: 11.5, h: 0.8, fontFace: "Cambria", fontSize: 30, bold: true, color: WHITE, isTextBox: true });
  const recs = [
    ["Deploy", "XGBoost on the raw target as the primary cost-prediction model (Overall scope); use Turvo/Magnus segment models where segment-level accuracy matters more than a unified pipeline"],
    ["Fix data capture", "Populate EquipmentType/Enclosed for Magnus shipments \u2014 would remove the need for imputation and likely close part of the Turvo\u2013Magnus R\u00b2 gap"],
    ["Extend to the tail", "Consider a hurdle or quantile-regression approach for the very-high-cost shipments removed by IQR outlier filtering, if the business needs those predictions too"],
    ["Retrain periodically", "Historical Lane Cost features are rolling time windows and Market Conditions are macro series \u2014 both will drift and need refresh"],
  ];
  let y = 1.65;
  recs.forEach((r) => {
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 0.42, h: 0.42, rectRadius: 0.21, fill: { color: GOLD }, line: { type: "none" } });
    s.addText("\u2713", { x: 0.7, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontSize: 16, bold: true, color: NAVY, isTextBox: true });
    s.addText(r[0], { x: 1.35, y: y - 0.05, w: 2.6, h: 0.6, fontFace: "Cambria", fontSize: 15, bold: true, color: ICE, isTextBox: true, valign: "top" });
    s.addText(r[1], { x: 4.05, y: y - 0.05, w: 8.6, h: 1.05, fontFace: "Calibri", fontSize: 13, color: "E4E8F7", isTextBox: true, valign: "top" });
    y += 1.28;
  });
  pageNum(s, 13);
}

pres.writeFile({ fileName: "/home/claude/proj/reports/Veltris_Vehicle_Cost_Model_Summary.pptx" })
  .then(() => console.log("pptx written"));
