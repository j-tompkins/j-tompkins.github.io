"""
01_eda.py
Purpose:
- Load ACE ds2748 CSV (aquatic rare species richness by HUC12)
- Produce quick, portfolio-ready figures

Why:
- EDA validates the data and gives you immediate visuals for your page
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Resolve paths relative to this script's location
BASE = Path(__file__).resolve().parents[1]                  # .../projects/species-richness
DATA = BASE / "data"
FIG  = BASE / "figures"
FIG.mkdir(exist_ok=True)

CSV_PATH = DATA / "ace_ds2748.csv"

def main():
    # Treat HUC12 as an ID (string) to avoid float/scientific notation issues and to enable joins later
    df = pd.read_csv(CSV_PATH, dtype={"HUC12": str})

    # 1) Rank distribution
    ax = df["RarAqRankSW"].value_counts().sort_index().plot(kind="bar")
    ax.set_title("Count of Watersheds by Rare Aquatic Species Rank (RarAqRankSW)")
    ax.set_xlabel("Rank (0–5, higher = richer)")
    ax.set_ylabel("Number of HUC12 Watersheds")
    plt.tight_layout()
    plt.savefig(FIG / "rank_counts.png", dpi=150)
    plt.close()

    # 2) Richness distribution
    ax = df["RarAqSumSW"].plot(kind="hist", bins=30)
    ax.set_title("Distribution of Normalized Rare Aquatic Richness (RarAqSumSW)")
    ax.set_xlabel("RarAqSumSW (0–1)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(FIG / "richness_hist.png", dpi=150)
    plt.close()

    # 3) Fish vs Amphibians
    plt.scatter(df["RarFish"], df["RarAqAmph"])
    plt.title("Rare Fish vs Rare Amphibians by Watershed")
    plt.xlabel("RarFish (count)")
    plt.ylabel("RarAqAmph (count)")
    plt.tight_layout()
    plt.savefig(FIG / "scatter_fish_vs_amph.png", dpi=150)
    plt.close()

    # 4) Fish vs Reptiles
    plt.scatter(df["RarFish"], df["RarAqRept"])
    plt.title("Rare Fish vs Rare Reptiles by Watershed")
    plt.xlabel("RarFish (count)")
    plt.ylabel("RarAqRept (count)")
    plt.tight_layout()
    plt.savefig(FIG / "scatter_fish_vs_rept.png", dpi=150)
    plt.close()

    # 5) Top 15 watersheds by normalized richness
    topN = 15
    top = df.nlargest(topN, "RarAqSumSW")[["Name", "RarAqSumSW"]].copy()
    ax = top.plot(kind="bar", x="Name", y="RarAqSumSW", legend=False, figsize=(10, 6))
    ax.set_title(f"Top {topN} Watersheds by Normalized Rare Aquatic Richness")
    ax.set_xlabel("Watershed (HUC12 Name)")
    ax.set_ylabel("RarAqSumSW")
    ax.tick_params(axis="x", rotation=60)
    plt.tight_layout()
    plt.savefig(FIG / "top_richness_bar.png", dpi=150)
    plt.close()

    # Handy table for captions/labels later
    df.nlargest(10, "RarAqSumSW")[
        ["HUC12", "Name", "RarAqSumSW", "RarFish", "RarAqAmph", "RarAqRept"]
    ].to_csv(BASE / "top10_watersheds.csv", index=False)

    print("EDA complete. Images saved in ./figures")

if __name__ == "__main__":
    main()