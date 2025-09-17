# src/train_model.py
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from joblib import dump

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score, average_precision_score,
    precision_recall_curve
)

from config import data_processed, img_dir, model_path

def main():
    # Load processed CSV
    df = pd.read_csv(data_processed)

    # Target + predictors + weights
    y = df["homeless"]
    X = df.drop(columns=["homeless", "num_visits"])
    w = df["num_visits"]

    # Train/test split
    X_tr, X_te, y_tr, y_te, w_tr, w_te = train_test_split(
        X, y, w, test_size=0.2, random_state=42, stratify=y
    )

    # Columns for dummy coding
    categorical_features = ["hpi_rank", "visit_type", "category",
                            "demographics", "diagnosis", "Year"]

    preproc = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)],
        remainder="drop",
    )

    # Logistic Regression (balanced)
    logreg = LogisticRegression(max_iter=1000, solver="lbfgs", class_weight="balanced")
    pipe = Pipeline([("prep", preproc), ("model", logreg)])

    # Fit with sample weights (respect aggregated counts)
    pipe.fit(X_tr, y_tr, model__sample_weight=w_tr)

    # Default metrics
    y_pred = pipe.predict(X_te)
    print("\n=== Classification Report (default threshold) ===")
    print(classification_report(y_te, y_pred))

    if hasattr(pipe.named_steps["model"], "predict_proba"):
        y_prob = pipe.predict_proba(X_te)[:, 1]
        y_true_bin = (y_te.astype(str) == "Homeless").astype(int)
        print("ROC-AUC:", roc_auc_score(y_true_bin, y_prob))
        print("PR-AUC :", average_precision_score(y_true_bin, y_prob))

        # Threshold tuning (maximize F1)
        prec, rec, thr = precision_recall_curve(y_true_bin, y_prob)
        f1_vals = 2 * (prec[:-1] * rec[:-1]) / (prec[:-1] + rec[:-1] + 1e-12)
        best_idx = f1_vals.argmax()
        best_thresh = thr[best_idx]
        print(f"\nBest F1 threshold: {best_thresh:.3f} | "
              f"F1={f1_vals[best_idx]:.3f} | "
              f"Precision={prec[best_idx]:.3f} | "
              f"Recall={rec[best_idx]:.3f}")

        y_pred_custom = np.where(y_prob >= best_thresh, "Homeless", "Not Homeless")
        print("\n=== Classification Report (custom threshold) ===")
        print(classification_report(y_te.astype(str), y_pred_custom))

    # ---------- Coefficients figure (interpretability) ----------
    prep = pipe.named_steps["prep"]
    est = pipe.named_steps["model"]

    ohe = prep.named_transformers_["cat"]
    feature_names = ohe.get_feature_names_out(categorical_features)

    classes = est.classes_
    pos_idx = np.where(classes.astype(str) == "Homeless")[0]
    if len(pos_idx) == 0:
        coef = est.coef_.ravel()
    else:
        coef = est.coef_[pos_idx[0], :]

    coef_series = pd.Series(coef, index=feature_names).sort_values()
    top_k = 12
    top_neg = coef_series.head(top_k)
    top_pos = coef_series.tail(top_k)
    to_plot = pd.concat([top_neg, top_pos])

    plt.figure()
    plt.barh(to_plot.index, to_plot.values)
    plt.axvline(0, linewidth=1)
    plt.title("Logistic Regression Coefficients (positive → more likely Homeless)")
    plt.tight_layout()
    out = img_dir / "lr_coefficients_top_features.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out}")

    # ---------- Optional: RandomForest sanity-check ----------
    try:
        rf = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)
        pipe_rf = Pipeline([("prep", preproc), ("model", rf)])
        pipe_rf.fit(X_tr, y_tr, model__sample_weight=w_tr)
        print("\n=== RandomForest Classification Report ===")
        print(classification_report(y_te, pipe_rf.predict(X_te)))
    except Exception as e:
        print(f"[INFO] RF baseline skipped: {e}")

    # Save LR pipeline
    dump(pipe, model_path)
    print(f"\nSaved LogisticRegression model → {model_path}")

if __name__ == "__main__":
    main()
