import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path

st.set_page_config(page_title="Yield Predictor", layout="wide")


BASE = Path(".")
REPORT_DIR = BASE / "reports"
CHECKPOINT_DIR = BASE / "checkpoints"
MODEL_PATHS = [
    CHECKPOINT_DIR / "best_pipeline_xgb.pkl",
    BASE / "models" / "best_pipeline_xgb.pkl",
    BASE / "models" / "pipeline_yield.pkl",
]

@st.cache_resource
def load_saved_model():
    for p in MODEL_PATHS:
        if p.exists():
            try:
                obj = joblib.load(p)
                # obj may be either a pipeline or a dict with "pipeline" key
                if isinstance(obj, dict) and "pipeline" in obj:
                    return obj
                elif hasattr(obj, "predict"):
                    return {"pipeline": obj}
            except Exception as e:
                st.warning(f"Failed to load {p}: {e}")
    return None

def display_reports():
    st.header("Saved reports & plots")
    cols = st.columns(3)
    images = [
        REPORT_DIR / "pred_vs_actual_test.png",
        REPORT_DIR / "feature_importances.png",
        REPORT_DIR / "correlation_matrix.png",
        REPORT_DIR / "boxplots_numeric.png",
        REPORT_DIR / "accuracy_curve.png",
        REPORT_DIR / "loss_curve.png",
    ]
    # show thumbnails if exist
    for i, img in enumerate(images):
        if img.exists():
            with cols[i % 3]:
                st.image(str(img), use_column_width=True, caption=img.name)
    # show metrics table if present
    metrics_csv = REPORT_DIR / "metrics.csv"
    if metrics_csv.exists():
        st.subheader("Metrics")
        metrics_df = pd.read_csv(metrics_csv)
        st.table(metrics_df.set_index("split"))
    # feature importance table
    fi_csv = REPORT_DIR / "feature_importances.csv"
    if fi_csv.exists():
        st.subheader("Top feature importances")
        fi = pd.read_csv(fi_csv)
        st.dataframe(fi.head(50))

def safe_engineer(df):
    # replicate the same simple engineered features used during training
    df = df.copy()
    # yield_per_area requires Production and Area
    if ("Production" in df.columns) and ("Area" in df.columns):
        df["yield_per_area"] = df["Production"] / (df["Area"].replace(0, np.nan))
        df["yield_per_area"] = df["yield_per_area"].fillna(0)
    if ("Fertilizer" in df.columns) and ("Area" in df.columns):
        df["fert_per_area"] = df["Fertilizer"] / (df["Area"].replace(0, np.nan))
        df["fert_per_area"] = df["fert_per_area"].fillna(0)
    if ("Pesticide" in df.columns) and ("Area" in df.columns):
        df["pest_per_area"] = df["Pesticide"] / (df["Area"].replace(0, np.nan))
        df["pest_per_area"] = df["pest_per_area"].fillna(0)
    if ("Annual_Rainfall" in df.columns) and ("Fertilizer" in df.columns):
        df["rain_x_fert"] = df["Annual_Rainfall"] * df["Fertilizer"]
    if "Crop_Year" in df.columns:
        try:
            df["year_from"] = df["Crop_Year"] - int(df["Crop_Year"].min())
        except Exception:
            df["year_from"] = 0
    return df

def align_with_training(df, save_obj):
    # save_obj may contain metadata keys used in training
    numeric_cols = save_obj.get("numeric_columns") or []
    categorical_cols = save_obj.get("categorical_columns") or []
    engineered = save_obj.get("engineered_features") or []
    target = save_obj.get("target")  # usually "Yield"
    applied_log = save_obj.get("applied_log_target", False)

    # Ensure engineered present if possible
    df = safe_engineer(df)

    # Fill missing raw columns expected by training
    expected_raw = list(set(numeric_cols + categorical_cols))
    for c in expected_raw:
        if c not in df.columns:
            if c in numeric_cols:
                df[c] = 0.0
            else:
                df[c] = "__missing__"

    # If pipeline expects columns in a specific order, ColumnTransformer handles selection.
    # Convert types: attempt numeric casting for numeric columns
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    # Ensure final order contains expected columns (pipeline will drop extra columns)
    return df, applied_log

def predict_dataframe(df_in, save_obj):
    pipeline = save_obj.get("pipeline") if isinstance(save_obj, dict) else save_obj
    df, applied_log = align_with_training(df_in, save_obj)
    # select only the raw columns - pipeline's preprocessor will select correct ones
    preds = pipeline.predict(df)
    if applied_log:
        preds = np.expm1(preds)
    return preds

# ---------- Streamlit UI ----------
st.title("Crop Yield Prediction — Streamlit UI")

save_obj = load_saved_model()
if save_obj is None:
    st.error("No saved pipeline found. Make sure models/checkpoints exist.")
    st.stop()

st.sidebar.header("Model info")
st.sidebar.write("Loaded model from checkpoint.")
st.sidebar.json({k: v for k, v in save_obj.items() if k in ("numeric_columns", "categorical_columns", "engineered_features", "target", "applied_log_target")})

display_reports()

st.write("---")
st.header("Predict on new data")

uploaded = st.file_uploader("Upload CSV with new rows (raw columns should match training raw columns)", type=["csv"])
single_row_mode = st.checkbox("Or enter a single row manually", value=False)

if uploaded is None and not single_row_mode:
    st.info("Upload a CSV or use manual input to get predictions.")
else:
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            st.write(f"Uploaded {new_df.shape[0]} rows. Preview:")
            st.dataframe(new_df.head())
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
            new_df = None
    else:
        # manual single-row inputs: render inputs for expected raw columns
        st.info("Fill the fields for a single example. Fields shown are from training metadata.")
        numeric_cols = save_obj.get("numeric_columns") or []
        categorical_cols = save_obj.get("categorical_columns") or []
        inputs = {}
        with st.form("single_row"):
            for c in numeric_cols[:10]:   # show up to 10 numeric in form to avoid overflow
                inputs[c] = st.number_input(f"{c} (numeric)", value=0.0, key=f"num_{c}")
            for c in categorical_cols[:10]:
                inputs[c] = st.text_input(f"{c} (categorical)", value="__missing__", key=f"cat_{c}")
            submitted = st.form_submit_button("Create single-row CSV")
        if submitted:
            new_df = pd.DataFrame([inputs])
            st.write("Manual row:")
            st.dataframe(new_df)

    if new_df is not None:
        # Predict button
        if st.button("Run predictions"):
            try:
                df_prepared, applied_log = align_with_training(new_df, save_obj)
                preds = predict_dataframe(df_prepared, save_obj)
                out = new_df.copy().reset_index(drop=True)
                out["predicted_Yield"] = preds
                st.success("Predictions complete")
                st.dataframe(out.head(50))
                # download
                csv_bytes = out.to_csv(index=False).encode("utf-8")
                st.download_button("Download predictions CSV", csv_bytes, "predictions.csv", "text/csv")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

st.write("---")
st.header("Checkpoint & saved files")
# list files in checkpoints and reports
def list_files(folder):
    folder = Path(folder)
    if not folder.exists(): 
        return []
    return sorted([str(p.relative_to(folder.parent)) for p in folder.glob("*") if p.is_file()])

st.subheader("Checkpoints")
for p in list_files(CHECKPOINT_DIR):
    st.write(p)

st.subheader("Reports")
for p in list_files(REPORT_DIR):
    st.write(p)

st.info("If upload/prediction fails, check that your CSV contains the same raw column NAMES (watch whitespace/case). The UI will attempt to engineer features automatically (yield_per_area, fert_per_area, etc.) where possible.")
