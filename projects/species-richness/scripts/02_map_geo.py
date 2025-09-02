"""
02_map_geo.py
Purpose:
- Read a HUC12 vector layer (GeoJSON/GeoPackage/Shapefile) from disk
- If the layer already has ACE ds2748 fields (RarAqRankSW, RarAqSumSW, etc.), plot directly
- Otherwise, join the ACE ds2748 CSV on HUC12, then plot
- Export two choropleths: rarity rank (categorical) and normalized richness (continuous)

Why this version?
- Works with BOTH scenarios:
  1) GeoJSON that already includes the ACE attributes (no join needed)
  2) A plain HUC12 boundary file + your CSV (join on HUC12)

Usage:
  python projects/species-richness/scripts/02_map_geo.py "C:/path/to/your/file.geojson"
  # Optional if HUC12 column in the vector file has a different name:
  # --huc-field HUC_12
"""

import sys
from pathlib import Path
import pandas as pd

try:
    import geopandas as gpd
except ImportError:
    print("GeoPandas is required for mapping. Install with:\n  pip install geopandas pyogrio shapely")
    sys.exit(1)

# ---- Project paths (relative to repo structure) ----
BASE = Path(__file__).resolve().parents[1]                 # .../projects/species-richness
DATA = BASE / "data"
FIG  = BASE / "figures"
FIG.mkdir(exist_ok=True)

CSV_PATH = DATA / "ace_ds2748.csv"  # Your metrics CSV

# Columns that indicate the ACE richness attributes are already present
ACE_REQUIRED_COLS = {"RarAqRankSW", "RarAqSumSW", "RarFish", "RarAqAmph", "RarAqRept"}

def validate_vector_path(p: str) -> Path:
    """Ensure the given vector path exists; give helpful guidance if not."""
    path = Path(p)
    if not path.exists():
        print(f"\n[Path Error] I can’t find this file:\n  {p}\n")
        print("Tips:")
        print("- Confirm the exact filename and folder in File Explorer.")
        print("- Use quotes around paths with spaces.")
        print("- Use forward slashes (C:/Users/You/...) or double backslashes (C:\\\\Users\\\\You\\\\...).")
        sys.exit(1)
    return path

def guess_huc_field(cols):
    """Try to guess which column is the 12-digit hydrologic unit code (HUC12)."""
    if "HUC12" in cols:
        return "HUC12"
    candidates = [c for c in cols if c.upper() in {"HUC12", "HUC_12", "HUC_12_CODE"}]
    if candidates:
        return candidates[0]
    for c in cols:
        if "HUC" in c.upper() and "12" in c:
            return c
    return None

def main(vector_path: str, huc_field_arg: str | None):
    vec_path = str(validate_vector_path(vector_path))

    # Read the vector layer (GeoJSON/GPKG/SHP all supported)
    gdf = gpd.read_file(vec_path)
    cols = set(gdf.columns)

    # Case A: GeoJSON ALREADY HAS ACE attributes -> no join needed
    if ACE_REQUIRED_COLS.issubset(cols):
        print("[Info] ACE richness columns found in the GeoJSON. No join needed.")
        mg = gdf.copy()
    else:
        # Case B: we need to join with the CSV on HUC12
        print("[Info] ACE columns not found. Will join with CSV on HUC12.")
        # Determine HUC field in the vector data
        huc_field = huc_field_arg or guess_huc_field(list(gdf.columns))
        if not huc_field:
            print(f"\n[Join Error] Could not find a HUC12-like field in the vector layer.")
            print(f"Vector columns (first 15): {list(gdf.columns)[:15]}")
            print("Pass --huc-field FIELDNAME explicitly (e.g., --huc-field HUC_12).")
            sys.exit(1)

        # Normalize types for a clean join
        gdf[huc_field] = gdf[huc_field].astype(str).str.replace(".0", "", regex=False)

        # Read CSV and normalize HUC12
        df = pd.read_csv(CSV_PATH, dtype={"HUC12": str})
        df["HUC12"] = df["HUC12"].astype(str)

        # Perform left join to keep all geometries
        mg = gdf.merge(df, left_on=huc_field, right_on="HUC12", how="left")

        # Simple join quality check
        join_rate = mg["RarAqSumSW"].notna().mean()
        print(f"[Info] Join rate (fraction polygons matched): {join_rate:.3f}")

    print("CRS:", mg.crs)

    # Map 1: categorical rarity rank
    ax = mg.plot(column="RarAqRankSW", legend=True, figsize=(9, 9),
                 linewidth=0.2, edgecolor="black")
    ax.set_title("Rare Aquatic Species Rank by HUC12")
    ax.axis("off")
    ax.figure.tight_layout()
    ax.figure.savefig(FIG / "map_rank.png", dpi=150)
    ax.figure.clf()

    # Map 2: continuous richness
    ax = mg.plot(column="RarAqSumSW", legend=True, figsize=(9, 9),
                 linewidth=0.2, edgecolor="black")
    ax.set_title("Normalized Rare Aquatic Richness (RarAqSumSW) by HUC12")
    ax.axis("off")
    ax.figure.tight_layout()
    ax.figure.savefig(FIG / "map_richness.png", dpi=150)
    ax.figure.clf()

    print("Maps saved to ./figures (map_rank.png, map_richness.png)")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Plot ACE ds2748 maps from a GeoJSON (or join CSV if needed).")
    p.add_argument("vector_path", help="Path to GeoJSON/GPKG/SHP etc.")
    p.add_argument("--huc-field", help="Name of HUC12 field in vector data (if not 'HUC12')", default=None)
    args = p.parse_args()
    main(args.vector_path, args.huc_field)