"""
Step 3: EDA & visualization - relationship of the (VIF+Boruta) reduced
feature set with the target (TotalCost), organized by business feature group.
Saves PNG charts to artifacts/figures.
"""
import sys
sys.path.insert(0, "/home/claude/proj/src")
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from feature_groups import FEATURE_GROUPS

sns.set_style("whitegrid")
FIG_DIR = "/home/claude/proj/artifacts/figures"
DATA_DIR = "/home/claude/proj/data/processed"
TARGET = "TotalCost"

df = pd.read_parquet(f"{DATA_DIR}/veltris_reduced.parquet")
final_features = json.load(open(f"{DATA_DIR}/feature_selection_summary.json"))["final_features"]
print("Reduced data:", df.shape, "| features:", len(final_features))

# map each final feature to its group
feat_to_group = {}
for g, feats in FEATURE_GROUPS.items():
    for f in feats:
        feat_to_group[f] = g
group_of_feature = {f: feat_to_group.get(f, "Other") for f in final_features}
pd.Series(group_of_feature, name="group").to_csv(f"{DATA_DIR}/final_feature_group_mapping.csv")
print(pd.Series(group_of_feature).value_counts())

# ---------------------------------------------------------------------
# 1. Target distribution (raw dataset vs processed/outlier-removed)
# ---------------------------------------------------------------------
raw = pd.read_csv("/home/claude/raw_data.csv", low_memory=False, usecols=[TARGET])
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].hist(raw[TARGET].dropna(), bins=80, color="#4C72B0")
axes[0].set_title("TotalCost distribution - RAW dataset")
axes[0].set_xlabel("TotalCost ($)")
axes[1].hist(df[TARGET], bins=80, color="#55A868")
axes[1].set_title("TotalCost distribution - PROCESSED (outliers removed)")
axes[1].set_xlabel("TotalCost ($)")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/01_target_distribution_before_after.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 2. Correlation heatmap of final reduced features + target
# ---------------------------------------------------------------------
num_final = [f for f in final_features if df[f].dtype != "object"]
corr = df[num_final + [TARGET]].corr()
plt.figure(figsize=(13, 11))
sns.heatmap(corr, cmap="coolwarm", center=0, annot=False, square=True,
            cbar_kws={"shrink": 0.7})
plt.title("Correlation heatmap - reduced feature set vs TotalCost")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/02_correlation_heatmap_reduced.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 3. Correlation of each reduced feature with target, colored by group
# ---------------------------------------------------------------------
target_corr = corr[TARGET].drop(TARGET).sort_values()
colors = sns.color_palette("tab10", n_colors=len(FEATURE_GROUPS))
group_color_map = {g: colors[i] for i, g in enumerate(FEATURE_GROUPS.keys())}
bar_colors = [group_color_map.get(group_of_feature.get(f, "Other"), "grey") for f in target_corr.index]

plt.figure(figsize=(9, 8))
plt.barh(target_corr.index, target_corr.values, color=bar_colors)
plt.axvline(0, color="black", linewidth=0.8)
plt.title("Correlation of each selected feature with TotalCost\n(color = feature group)")
plt.xlabel("Pearson correlation with TotalCost")
handles = [plt.Rectangle((0, 0), 1, 1, color=group_color_map[g]) for g in FEATURE_GROUPS]
plt.legend(handles, FEATURE_GROUPS.keys(), bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/03_feature_target_correlation_by_group.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 4. Scatter/relationship plots for top 4 correlated features
# ---------------------------------------------------------------------
top_feats = target_corr.abs().sort_values(ascending=False).head(4).index.tolist()
fig, axes = plt.subplots(2, 2, figsize=(11, 9))
for ax, f in zip(axes.ravel(), top_feats):
    sample = df.sample(min(15000, len(df)), random_state=1)
    ax.hexbin(sample[f], sample[TARGET], gridsize=40, cmap="Blues", mincnt=1)
    ax.set_xlabel(f)
    ax.set_ylabel("TotalCost")
    ax.set_title(f"{f} vs TotalCost (r={corr.loc[f, TARGET]:.2f})")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/04_top_feature_relationships.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 5. Distance & lane-cost group relationship (business-relevant view)
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
sample = df.sample(min(20000, len(df)), random_state=1)
axes[0].hexbin(sample["HaversineMiles"], sample[TARGET], gridsize=40, cmap="Oranges", mincnt=1)
axes[0].set_title("Distance group: HaversineMiles vs TotalCost")
axes[0].set_xlabel("HaversineMiles"); axes[0].set_ylabel("TotalCost")
axes[1].hexbin(sample["TotalCostOriginMean"], sample[TARGET], gridsize=40, cmap="Greens", mincnt=1)
axes[1].set_title("Historical Lane Cost group: TotalCostOriginMean vs TotalCost")
axes[1].set_xlabel("TotalCostOriginMean"); axes[1].set_ylabel("TotalCost")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/05_distance_lanecost_relationships.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 6. Boxplot: TotalCost by EquipmentType (Equipment group) & OriginState top10 (Customer group)
# ---------------------------------------------------------------------
df_full_cleaned = pd.read_parquet(f"{DATA_DIR}/veltris_cleaned.parquet")
fig, axes = plt.subplots(1, 1, figsize=(9, 5))
order = df_full_cleaned.groupby("EquipmentType")[TARGET].median().sort_values().index
sns.boxplot(data=df_full_cleaned, x="EquipmentType", y=TARGET, order=order, ax=axes, showfliers=False)
axes.set_title("Equipment group: TotalCost by EquipmentType")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/06_equipment_type_cost.png", dpi=130)
plt.close()

# ---------------------------------------------------------------------
# 7. Group-level "average |correlation| with target" summary bar
# ---------------------------------------------------------------------
group_scores = {}
for g, feats in FEATURE_GROUPS.items():
    present = [f for f in feats if f in num_final]
    if present:
        group_scores[g] = corr.loc[present, TARGET].abs().mean()
if group_scores:
    gs = pd.Series(group_scores).sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    gs.plot(kind="bar", color=[group_color_map[g] for g in gs.index])
    plt.title("Average |correlation| with TotalCost by feature group\n(selected features only)")
    plt.ylabel("Mean |Pearson r|")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/07_group_level_avg_correlation.png", dpi=130)
    plt.close()

print("EDA figures saved to", FIG_DIR)
