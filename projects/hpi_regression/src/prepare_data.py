# src/prepare_data.py
import pandas as pd
from config import data_raw, data_processed

def main():
    df = pd.read_csv(data_raw)

    # Rename for clarity; keep Year
    df = df.rename(columns={
        "Encounter Setting": "visit_type",
        "Diagnosis Group": "diagnosis",
        "Residence": "homeless",
        "Count": "num_visits",
        "HPI Percentile Ranking": "hpi_rank",
        "Category": "category",
        "Category Description": "demographics",
    })

    # Drop id-like column if present
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    # Focus on the demographic categories you care about
    keep = {"Sex", "Race/Ethnicity Group", "Age Group"}
    df = df[df["category"].isin(keep)].copy()

    # Cast useful columns to string (good for dummy coding)
    for c in ["hpi_rank", "visit_type", "category", "demographics", "diagnosis", "homeless"]:
        df[c] = df[c].astype(str)

    # Save clean CSV
    df.to_csv(data_processed, index=False)
    print(f"Saved cleaned data → {data_processed} (rows={len(df)})")

if __name__ == "__main__":
    main()
