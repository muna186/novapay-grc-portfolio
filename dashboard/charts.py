# ============================================================
# NovaPay Pty Ltd — Risk Visualisation Module
# Author: Muna
# Purpose: Generates static PNG charts from the processed risk
#          register for embedding in README and reports.
#
# Charts produced:
#   1. Risk Heatmap (5x5 likelihood-impact matrix)
#   2. Risks by Rating (Critical/High/Medium/Low)
#   3. Top 10 Risks by Score
#   4. Risks by ISO 27001 Annex A Theme
#   5. Risks by Essential Eight Strategy
#   6. Risks by Regulatory Regime
#
# Output: PNG files saved to /visuals folder
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---- Load the processed dataset ----
df = pd.read_csv("data/novapay_risks_processed.csv")
print(f"Loaded {len(df)} processed risks for visualisation.")

# ---- Ensure the visuals folder exists ----
VISUALS_DIR = "visuals"
os.makedirs(VISUALS_DIR, exist_ok=True)


# ---- Define the NovaPay chart style (consistent across all charts) ----
sns.set_style("whitegrid")

# Colour palette aligned to risk severity conventions
RATING_COLOURS = {
    "Critical": "#C0392B",  # deep red
    "High":     "#E67E22",  # orange
    "Medium":   "#F1C40F",  # amber
    "Low":      "#27AE60",  # green
}

# Default figure settings
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["figure.autolayout"] = True

print("Chart styling configured.")

# ============================================================
# CHART 1 — RISK HEATMAP (5x5 likelihood-impact matrix)
# Purpose: Shows how risks cluster across the likelihood-impact
# space. Standard ISO 31000 visual for executive reporting.
# ============================================================

# Build a 5x5 grid counting risks at each (Likelihood, Impact) combination
heatmap_data = df.groupby(
    ["Inherent_Likelihood_1_5", "Inherent_Impact_1_5"]
).size().unstack(fill_value=0)

# Ensure the grid is a complete 5x5 even if some combinations have 0 risks
heatmap_data = heatmap_data.reindex(
    index=[1, 2, 3, 4, 5], columns=[1, 2, 3, 4, 5], fill_value=0
)

# Reverse the y-axis so Likelihood 5 (Almost Certain) appears at the top
heatmap_data = heatmap_data.sort_index(ascending=False)

# Build the chart
fig, ax = plt.subplots(figsize=(8, 6))

sns.heatmap(
    heatmap_data,
    annot=True,            # show numbers in each cell
    fmt="d",               # format numbers as integers
    cmap="Reds",           # red colour scale (more risks = darker)
    cbar_kws={"label": "Number of Risks"},
    linewidths=1,
    linecolor="white",
    ax=ax,
)

ax.set_title("NovaPay — Risk Heatmap (Inherent Risk)", pad=15)
ax.set_xlabel("Impact (1 = Negligible, 5 = Catastrophic)")
ax.set_ylabel("Likelihood (1 = Rare, 5 = Almost Certain)")

plt.savefig(f"{VISUALS_DIR}/01_risk_heatmap.png", bbox_inches="tight")
plt.close()

print("Chart 1 saved: 01_risk_heatmap.png")

# ============================================================
# CHART 2 — RISKS BY RATING
# Purpose: Bar chart showing distribution of risks across the
# four severity bands. Quick severity profile snapshot.
# ============================================================

# Count risks per rating, in severity order (not alphabetical)
rating_order = ["Critical", "High", "Medium", "Low"]
rating_counts = df["Calculated_Risk_Rating"].value_counts().reindex(
    rating_order, fill_value=0
)

# Build the chart
fig, ax = plt.subplots(figsize=(8, 5))

bar_colours = [RATING_COLOURS[r] for r in rating_order]
bars = ax.bar(rating_counts.index, rating_counts.values, color=bar_colours,
              edgecolor="black", linewidth=0.8)

# Annotate each bar with its value
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.15,
        f"{int(height)}",
        ha="center", va="bottom", fontweight="bold", fontsize=12,
    )

ax.set_title("NovaPay — Risk Count by Rating", pad=15)
ax.set_xlabel("Risk Rating")
ax.set_ylabel("Number of Risks")
ax.set_ylim(0, max(rating_counts.values) + 2)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig(f"{VISUALS_DIR}/02_risks_by_rating.png", bbox_inches="tight")
plt.close()

print("Chart 2 saved: 02_risks_by_rating.png")


# ============================================================
# CHART 3 — TOP 10 RISKS BY SCORE
# Purpose: Horizontal ranked bar chart. Shows the priority
# order for treatment. Most actionable single chart.
# ============================================================

# Take top 10 by calculated score; sort ascending so highest is at top
top_10 = df.nlargest(10, "Calculated_Risk_Score").sort_values(
    "Calculated_Risk_Score", ascending=True
)

# Map each risk to its rating colour
bar_colours = [RATING_COLOURS[r] for r in top_10["Calculated_Risk_Rating"]]

# Build the chart
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    top_10["Risk_ID"],
    top_10["Calculated_Risk_Score"],
    color=bar_colours,
    edgecolor="black",
    linewidth=0.6,
)

# Annotate each bar with its score
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.3,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va="center", fontweight="bold", fontsize=10,
    )

ax.set_title("NovaPay — Top 10 Risks by Calculated Score", pad=15)
ax.set_xlabel("Risk Score (Likelihood × Impact)")
ax.set_ylabel("Risk ID")
ax.set_xlim(0, 28)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Manual legend so the rating colours are explained
from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor=RATING_COLOURS[r], edgecolor="black", label=r)
    for r in ["Critical", "High", "Medium", "Low"]
]
ax.legend(handles=legend_handles, title="Rating", loc="lower right", frameon=True)

plt.savefig(f"{VISUALS_DIR}/03_top_10_risks.png", bbox_inches="tight")
plt.close()

print("Chart 3 saved: 03_top_10_risks.png")

# ============================================================
# HELPER — SPLIT AND COUNT MULTI-VALUE CELLS
# Purpose: Several columns contain multiple values per cell
# separated by semicolons (e.g. "A.8.2; A.8.5; A.5.3").
# This function explodes those into individual values and
# counts how many risks each one appears in.
# ============================================================

def count_multi_values(column, separator=";"):
    """
    Splits each cell in `column` by `separator`, strips whitespace,
    and counts how many risks reference each unique value.

    Returns a pandas Series sorted by count descending.
    """
    # Drop empty/NA cells, then split each cell into a list
    exploded = (
        column.dropna()
              .astype(str)
              .str.split(separator)
              .explode()
              .str.strip()
    )

    # Remove any empty strings produced by splitting
    exploded = exploded[exploded != ""]

    # Count occurrences and return sorted descending
    return exploded.value_counts()


print("Helper function ready: count_multi_values()")

# ============================================================
# CHART 4 — RISKS BY ISO 27001 ANNEX A THEME
# Purpose: Shows how risks distribute across the four Annex A
# control themes (Organisational, People, Physical,
# Technological). Anchors the analysis to the primary framework.
# ============================================================

# Annex A control number prefixes map to the four themes
# (per ISO/IEC 27001:2022 Annex A structure)
def classify_annex_a_theme(control_string):
    """
    Maps an Annex A control reference (e.g. 'A.8.2') to its theme.
    Theme prefixes per ISO 27001:2022:
        A.5.x = Organisational (37 controls)
        A.6.x = People (8 controls)
        A.7.x = Physical (14 controls)
        A.8.x = Technological (34 controls)
    """
    if "A.5." in control_string:
        return "Organisational"
    elif "A.6." in control_string:
        return "People"
    elif "A.7." in control_string:
        return "Physical"
    elif "A.8." in control_string:
        return "Technological"
    else:
        return "Other"


# Explode the Annex_A_Control column into individual control references
exploded_controls = (
    df["Annex_A_Control"]
      .dropna()
      .astype(str)
      .str.split(";")
      .explode()
      .str.strip()
)
exploded_controls = exploded_controls[exploded_controls != ""]

# Classify each control reference into its theme
themes = exploded_controls.apply(classify_annex_a_theme)
theme_counts = themes.value_counts()

# Force the canonical theme order
theme_order = ["Organisational", "People", "Physical", "Technological"]
theme_counts = theme_counts.reindex(theme_order, fill_value=0)

# Build the chart
fig, ax = plt.subplots(figsize=(9, 5))

theme_colours = ["#2E86AB", "#A23B72", "#F18F01", "#3B7A57"]
bars = ax.bar(
    theme_counts.index,
    theme_counts.values,
    color=theme_colours,
    edgecolor="black",
    linewidth=0.8,
)

# Annotate each bar with its count
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        f"{int(height)}",
        ha="center", va="bottom", fontweight="bold", fontsize=12,
    )

ax.set_title("NovaPay — Annex A Control References by Theme", pad=15)
ax.set_xlabel("ISO 27001:2022 Annex A Theme")
ax.set_ylabel("Number of Control References")
ax.set_ylim(0, max(theme_counts.values) + 3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig(f"{VISUALS_DIR}/04_annex_a_themes.png", bbox_inches="tight")
plt.close()

print("Chart 4 saved: 04_annex_a_themes.png")

# ============================================================
# CHART 5 — RISKS BY ESSENTIAL EIGHT STRATEGY
# Purpose: Shows how risks map to ASD's Essential Eight
# mitigation strategies. Australian-specific framework view.
# Note: Filters out N/A placeholder values to keep the chart
# accurate to the published Essential Eight strategy list.
# ============================================================

# Use the helper to count Essential Eight strategy occurrences
e8_counts = count_multi_values(df["Essential_Eight_Mapping"])

# Filter to only the eight valid Essential Eight strategies
# (Source: ASD Essential Eight Maturity Model — ACSC)
valid_e8_strategies = [
    "Application Control",
    "Patch Applications",
    "Configure Microsoft Office Macro Settings",
    "User Application Hardening",
    "Restrict Administrative Privileges",
    "Patch Operating Systems",
    "Multi-Factor Authentication",
    "Regular Backups",
]
e8_counts = e8_counts[e8_counts.index.isin(valid_e8_strategies)]

# Sort ascending for horizontal bar (top of chart = highest count)
e8_counts = e8_counts.sort_values(ascending=True)

# Build the chart (horizontal — strategy names are long)
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    e8_counts.index,
    e8_counts.values,
    color="#1F4E79",  # ACSC navy blue — visual reference to ASD branding palette
    edgecolor="black",
    linewidth=0.6,
)

# Annotate each bar with its count
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.05,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va="center", fontweight="bold", fontsize=11,
    )

ax.set_title("NovaPay — Risks Mapped to Essential Eight Strategies", pad=15)
ax.set_xlabel("Number of Risks Referencing Strategy")
ax.set_ylabel("Essential Eight Mitigation Strategy")
ax.set_xlim(0, max(e8_counts.values) + 1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig(f"{VISUALS_DIR}/05_essential_eight.png", bbox_inches="tight")
plt.close()

print("Chart 5 saved: 05_essential_eight.png")

# ============================================================
# CHART 6 — RISKS BY REGULATORY REGIME
# Purpose: Shows how risks distribute across the Australian
# regulatory landscape. The compliance exposure view —
# essential framing for fintech engagements.
# Note: Normalises detailed regulatory references back to
# their parent regime (e.g. "APRA CPS 234 s.15" → "APRA CPS 234").
# ============================================================

def normalise_regulatory_flag(flag):
    """
    Maps a detailed regulatory reference to its parent regime.
    Source register includes section-level detail (e.g. APRA CPS 234 s.15)
    which is too granular for an executive view.
    """
    flag = flag.strip()

    if "APRA CPS 234" in flag:
        return "APRA CPS 234"
    elif "APRA CPS 230" in flag:
        return "APRA CPS 230"
    elif "ASIC RG 255" in flag:
        return "ASIC RG 255"
    elif "Privacy Act" in flag and "Part IIIA" in flag:
        return "Privacy Act — Part IIIA"
    elif "Privacy Act" in flag:
        return "Privacy Act — APPs"
    elif "NDB" in flag:
        return "NDB Scheme"
    elif "Corporations Act" in flag:
        return "Corporations Act 2001"
    elif "Criminal Code" in flag:
        return "Criminal Code Act 1995"
    elif "AFSL" in flag:
        return "AFSL Conditions"
    else:
        return flag  # unknown — keep as-is for visibility


# Explode the regulatory flag column into individual references
exploded_regs = (
    df["Regulatory_Flag"]
      .dropna()
      .astype(str)
      .str.split(";")
      .explode()
      .str.strip()
)
exploded_regs = exploded_regs[exploded_regs != ""]

# Normalise to parent regime
normalised_regs = exploded_regs.apply(normalise_regulatory_flag)
reg_counts = normalised_regs.value_counts().sort_values(ascending=True)

# Build the chart (horizontal — regime names are long)
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    reg_counts.index,
    reg_counts.values,
    color="#5B2C6F",  # deep purple — distinct from rating and E8 palettes
    edgecolor="black",
    linewidth=0.6,
)

# Annotate each bar with its count
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.1,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va="center", fontweight="bold", fontsize=11,
    )

ax.set_title("NovaPay — Risks Mapped to Regulatory Regimes", pad=15)
ax.set_xlabel("Number of Risks Referencing Regime")
ax.set_ylabel("Regulatory Regime")
ax.set_xlim(0, max(reg_counts.values) + 1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig(f"{VISUALS_DIR}/06_regulatory_exposure.png", bbox_inches="tight")
plt.close()

print("Chart 6 saved: 06_regulatory_exposure.png")

# ============================================================
# COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("DASHBOARD GENERATION COMPLETE")
print("=" * 60)
print(f"\nAll charts saved to: /{VISUALS_DIR}/")
print("\nChart inventory:")
print("  01_risk_heatmap.png         — Likelihood-Impact matrix")
print("  02_risks_by_rating.png      — Severity distribution")
print("  03_top_10_risks.png         — Priority ranking")
print("  04_annex_a_themes.png       — ISO 27001 theme view")
print("  05_essential_eight.png      — ASD Essential Eight view")
print("  06_regulatory_exposure.png  — Australian regulatory view")
print("\nReady for embedding in README.")
print("=" * 60)