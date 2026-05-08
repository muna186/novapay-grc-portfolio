# ============================================================
# NovaPay Pty Ltd — Risk Pipeline
# Author: Muna
# Purpose: Reads raw risk register, calculates risk scores,
#          categorises risks, and outputs a processed dataset
#          for dashboard consumption.
#
# Risk scoring methodology: ISO 31000:2018 (Likelihood × Impact)
# Source register frameworks: ISO/IEC 27001:2022 (Annex A),
#   ASD Essential Eight, Privacy Act 1988 (Cth) inc. Part IIIA,
#   ASIC RG 255, APRA CPS 234 (future state), NDB Scheme
# ============================================================

import pandas as pd #tells Python: "load the pandas library so I can use it in this script."

# ---- Step 1: Load the raw risk register ----

df = pd.read_csv("data/novapay_risks_v2.csv")

print(f"Loaded {len(df)} risks from the register.") 
print(f"Columns found: {list(df.columns)}") 

# ---- Step 2: Calculate the inherent risk score ----
df["Calculated_Risk_Score"] = df["Inherent_Likelihood_1_5"] * df["Inherent_Impact_1_5"]

# ---- Step 3: Categorise each risk into a rating band ----

def categorise_risk(score):
    """
    Maps a numerical risk score to a rating band.
    Bands per NovaPay v6 GRC Agent specification (ISO 31000 aligned):
        1-6   = Low
        7-12  = Medium
        13-19 = High
        20-25 = Critical
    """
    if score <= 6:
        return "Low"
    elif score <= 12:
        return "Medium"
    elif score <= 19:
        return "High"
    else:
        return "Critical"


df["Calculated_Risk_Rating"] = df["Calculated_Risk_Score"].apply(categorise_risk)

# ---- Step 4: Save the processed dataset ----
output_path = "data/novapay_risks_processed.csv"
df.to_csv(output_path, index=False)
print(f"\nProcessed dataset saved to: {output_path}")

# ---- Step 5: Print a summary for the consultant ----
print("\n" + "=" * 60)
print("NOVAPAY RISK PIPELINE — SUMMARY")
print("=" * 60)

print(f"\nTotal risks processed: {len(df)}")

print("\nRisk count by rating:")
rating_counts = df["Calculated_Risk_Rating"].value_counts()
for rating, count in rating_counts.items():
    print(f"  {rating:<10} {count}")

print(f"\nHighest risk score: {df['Calculated_Risk_Score'].max()}")
print(f"Lowest risk score:  {df['Calculated_Risk_Score'].min()}")
print(f"Average risk score: {df['Calculated_Risk_Score'].mean():.1f}")

print("\nTop 3 risks by score:")
top_3 = df.nlargest(3, "Calculated_Risk_Score")[
    ["Risk_ID", "Calculated_Risk_Score", "Calculated_Risk_Rating"]
]
print(top_3.to_string(index=False))

print("\n" + "=" * 60)
print("Pipeline complete.")
print("=" * 60)





