# predict.py
"""
Predict script:
- Loads saved pipeline object (pipeline + metadata)
- Loads new_rows.csv (raw columns, same names as training raw columns)
- Adds any missing raw columns with sensible defaults (numeric -> 0, categorical -> "__missing__")
- Uses pipeline.predict(new_df_raw) to produce preds
- Saves new CSV with predicted_Yield column
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ---------- CONFIG ----------
MODEL_PATH = r"models/pipeline_yield.pkl"         # path saved by train.py
NEW_DATA_CSV = r"data/new_rows.csv"               # input: raw new rows (same raw columns as training)
OUT_CSV = r"data/new_rows_with_predictions.csv"
# ----------------------------

if not os.path.exists(MODEL_PATH):
    print(f"ERROR: model not found at: {MODEL_PATH}")
    sys.exit(1)

if not os.path.exists(NEW_DATA_CSV):
    print(f"ERROR: new data CSV not found at: {NEW_DATA_CSV}")
    sys.exit(1)

obj = joblib.load(MODEL_PATH)
pipeline = obj.get("pipeline")
numeric_cols = obj.get("numeric_columns", [])
categorical_cols = obj.get("categorical_columns", [])
raw_feature_cols = numeric_cols + categorical_cols

if pipeline is None:
    print("ERROR: pipeline not found inside saved object. Saved keys:", list(obj.keys()))
    sys.exit(1)

# Read new rows
new_df = pd.read_csv(NEW_DATA_CSV)
new_df.columns = new_df.columns.str.strip()

print("New data columns:", new_df.columns.tolist())

# Ensure raw_feature_cols are present; if missing add sensible defaults
missing_cols = [c for c in raw_feature_cols if c not in new_df.columns]
if missing_cols:
    print("Warning: missing expected raw training columns in new data:", missing_cols)
    for c in missing_cols:
        if c in numeric_cols:
            new_df[c] = 0.0
        else:
            new_df[c] = "__missing__"

# Extra columns in new_df are ignored by pipeline if preprocessor was built with remainder='drop'
# Reorder columns to the original raw order (safe)
try:
    new_df_ordered = new_df[raw_feature_cols].copy()
except Exception as e:
    print("Failed to reorder new_df to expected columns:", e)
    # fallback to using all columns (pipeline will select used ones)
    new_df_ordered = new_df.copy()

# Predict using pipeline (handles preprocessing)
try:
    preds = pipeline.predict(new_df_ordered)
except Exception as e:
    print("Prediction failed:", e)
    # try coercing numeric columns to numeric types (common dtype-mismatch)
    for c in numeric_cols:
        if c in new_df_ordered.columns:
            new_df_ordered[c] = pd.to_numeric(new_df_ordered[c], errors="coerce").fillna(0.0)
    preds = pipeline.predict(new_df_ordered)

# Attach predictions and save
out_df = new_df.copy().reset_index(drop=True)
out_df["predicted_" + obj.get("target", "y")] = preds
Path(os.path.dirname(OUT_CSV) or ".").mkdir(parents=True, exist_ok=True)
out_df.to_csv(OUT_CSV, index=False)
print("Saved predictions to:", OUT_CSV)
print(out_df.head())
