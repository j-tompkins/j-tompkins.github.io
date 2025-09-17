# src/config.py
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for scripts

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# RAW/PROCESSED
data_raw = ROOT / "data" / "raw" / "cal_hpi_data.csv"
data_processed = ROOT / "data" / "processed" / "hpi_clean.csv"

# OUTPUTS
img_dir = ROOT / "img"
model_path = ROOT / "data" / "processed" / "homeless_logreg.pkl"

# Ensure dirs
img_dir.mkdir(parents=True, exist_ok=True)
data_processed.parent.mkdir(parents=True, exist_ok=True)
