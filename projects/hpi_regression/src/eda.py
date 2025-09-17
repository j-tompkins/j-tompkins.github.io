# src/eda.py
import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt
from config import data_processed, img_dir

def plot_hpi_homeless(df):
    grp = df.groupby(["hpi_rank", "homeless"], as_index=False)["num_visits"].sum()
    grp["share"] = grp["num_visits"] / grp.groupby("hpi_rank")["num_visits"].transform("sum")

    plt.figure()
    for label in sorted(grp["homeless"].unique()):
        sub = grp[grp["homeless"] == label]
        plt.bar(sub["hpi_rank"], sub["share"], label=str(label))
    plt.xlabel("HPI Percentile Ranking")
    plt.ylabel("Share within HPI quartile")
    plt.title("Encounter Share by HPI Quartile and Homeless Status")
    plt.legend()
    plt.xticks(rotation=15)
    plt.tight_layout()
    out = img_dir / "hpi_homeless_share.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out}")

def plot_dx_by_hpi(df):
    dx = df.groupby(["hpi_rank", "diagnosis"], as_index=False)["num_visits"].sum()
    dx["hpi_total"] = dx.groupby("hpi_rank")["num_visits"].transform("sum")
    dx["share"] = dx["num_visits"] / dx["hpi_total"]

    for hpi in sorted(dx["hpi_rank"].unique()):
        sub = dx[dx["hpi_rank"] == hpi]
        plt.figure()
        plt.bar(sub["diagnosis"].astype(str), sub["share"])
        plt.title(f"Diagnosis Composition within {hpi}")
        plt.xlabel("Diagnosis Group")
        plt.ylabel("Share within HPI quartile")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        out = img_dir / f"diagnosis_composition_{str(hpi).replace(' ','_').replace('/','_')}.png"
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved {out}")

def plot_hpi_homeless_by_visit(df):
    vt = df.groupby(["visit_type", "hpi_rank", "homeless"], as_index=False)["num_visits"].sum()
    vt["hpi_total_by_vt"] = vt.groupby(["visit_type", "hpi_rank"])["num_visits"].transform("sum")
    vt["share"] = vt["num_visits"] / vt["hpi_total_by_vt"]

    for v in sorted(vt["visit_type"].unique()):
        sub = vt[vt["visit_type"] == v]
        plt.figure()
        for label in sorted(sub["homeless"].unique()):
            ss = sub[sub["homeless"] == label]
            plt.bar(ss["hpi_rank"], ss["share"], label=str(label))
        plt.title(f"HPI × Homeless Shares within {v}")
        plt.xlabel("HPI Percentile Ranking")
        plt.ylabel("Share within HPI & Visit Type")
        plt.legend()
        plt.xticks(rotation=15)
        plt.tight_layout()
        out = img_dir / f"hpi_homeless_share_{str(v).replace(' ','_')}.png"
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved {out}")

def main():
    df = pd.read_csv(data_processed)
    plot_hpi_homeless(df)
    plot_dx_by_hpi(df)
    plot_hpi_homeless_by_visit(df)

if __name__ == "__main__":
    main()
