# streamlit_crop_full.py
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
import io
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Any
from fpdf import FPDF     # new
import os                 # new

# ---------- CONFIG ----------
MODEL_PATH = Path("models/pipeline_yield.pkl")
DEFAULT_CSV = Path("crop_yield.csv")

# ---------- HELPERS ----------
@st.cache_resource
def load_pipeline(path: Path):
    try:
        return joblib.load(path)
    except Exception as e:
        return e

@st.cache_data
def read_csv_from_path(path: Path):
    return pd.read_csv(path)

@st.cache_data
def read_csv_from_buffer(buf: io.BytesIO):
    buf.seek(0)
    return pd.read_csv(buf)

def ensure_expected_columns(df: pd.DataFrame):
    expected = {
        "Crop","Crop_Year","Season","State","Area",
        "Production","Annual_Rainfall","Fertilizer","Pesticide"
    }
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

def parse_int_safe(v, fallback):
    try:
        return int(float(v))
    except:
        return fallback

def parse_float_safe(v, fallback):
    try:
        return float(v)
    except:
        return fallback

def find_yield_column(df: pd.DataFrame):
    for col in df.columns:
        if "yield" in col.lower():
            return col
    return None

def safe_linear_fit(x, y):
    try:
        x = np.array(x).reshape(-1, 1)
        y = np.array(y)
        model = LinearRegression().fit(x, y)
        return model.coef_[0], model.intercept_
    except Exception:
        return None, None

def normalize_prediction(pred_raw: Any) -> float:
    """
    Accept many possible predict outputs and return a single float.
    Raises TypeError if cannot normalize.
    """
    if isinstance(pred_raw, (list, tuple, np.ndarray)):
        return float(pred_raw[0])
    if isinstance(pred_raw, pd.Series):
        return float(pred_raw.iloc[0])
    if isinstance(pred_raw, (int, float, np.number)):
        return float(pred_raw)
    # try indexing
    try:
        return float(pred_raw[0])
    except Exception:
        raise TypeError("Predict returned unexpected type: " + str(type(pred_raw)))

# ---------- UI ----------
st.set_page_config(page_title="AgroPredict ML — Crop Yield Forecast Engine", layout="wide")
st.markdown("<h1 style='font-family:Inter, sans-serif;'>AgroPredict ML</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:-10px;color:#6b7280;font-size:16px;'>Crop Yield Forecast Engine — ML-driven agronomic insights & visualizations</div>", unsafe_allow_html=True)

# ---------- Load Model ----------
loaded = load_pipeline(MODEL_PATH)
if isinstance(loaded, Exception):
    st.error(f"Failed to load model file at: {MODEL_PATH}")
    st.exception(loaded)
    st.stop()

# If the loaded object is a dict and it contains the pipeline under 'pipeline', extract it.
pipeline = None
if isinstance(loaded, dict):
    if "pipeline" in loaded and hasattr(loaded["pipeline"], "predict"):
        pipeline = loaded["pipeline"]
    else:
        # try common keys
        for key in ["model", "estimator", "clf", "regressor", "best_estimator"]:
            if key in loaded and hasattr(loaded[key], "predict"):
                pipeline = loaded[key]
                break
        # fallback: scan values for first object with predict
        if pipeline is None:
            for v in loaded.values():
                if hasattr(v, "predict") and callable(getattr(v, "predict")):
                    pipeline = v
                    break
else:
    # if loaded object directly has predict, use it
    if hasattr(loaded, "predict") and callable(getattr(loaded, "predict")):
        pipeline = loaded

if pipeline is None:
    st.error("Loaded file does not contain a usable estimator with .predict().")
    st.info("If you saved extra metadata (a dict), re-save the estimator alone with: joblib.dump(estimator, 'models/pipeline_yield.pkl')")
    st.stop()

# ---------- Load Dataset ----------
df = None
if DEFAULT_CSV.exists():
    try:
        df = read_csv_from_path(DEFAULT_CSV)
    except Exception as e:
        st.error(f"Failed to read CSV at {DEFAULT_CSV}.")
        st.exception(e)
        st.stop()
else:
    uploaded = st.file_uploader("Upload crop_yield.csv", type=["csv"])
    if uploaded:
        try:
            df = read_csv_from_buffer(uploaded)
        except Exception as e:
            st.error("Failed to read uploaded CSV.")
            st.exception(e)
            st.stop()
    else:
        st.info("Upload a dataset to continue.")
        st.stop()

# Validate
try:
    ensure_expected_columns(df)
except Exception as e:
    st.error("Dataset validation failed:")
    st.exception(e)
    st.stop()

# Clean strings
df["Crop"] = df["Crop"].astype(str).str.strip()
df["State"] = df["State"].astype(str).str.strip()
df["Season"] = df["Season"].astype(str).str.strip()

# Detect optional yield column
yield_col = find_yield_column(df)
if yield_col:
    st.caption(f"Detected observed yield column in dataset: `{yield_col}`")
else:
    st.caption("No observed yield column detected in dataset. The app will compute and display model predictions only.")

# ---------- DROPDOWN WITHOUT INDEX ----------
option_labels = []
option_rows = []
for idx, row in df.iterrows():
    option_labels.append(f"{row['Crop']} / {row['State']}")
    option_rows.append(idx)

st.caption(f"Dropdown shows all CSV rows (duplicates preserved): {len(option_labels)} rows")
selected_label = st.selectbox("Select Crop / State", ["-- choose row --"] + option_labels)
if selected_label == "-- choose row --":
    st.stop()

selected_index = option_rows[option_labels.index(selected_label)]
row = df.loc[selected_index]

# Extract fields
crop_val = str(row["Crop"])
state_val = str(row["State"])
season_val = str(row["Season"])
crop_year_val = parse_int_safe(row["Crop_Year"], 0)
area_val = parse_float_safe(row["Area"], 0.0)
production_val = parse_float_safe(row["Production"], 0.0)
rain_val = parse_float_safe(row["Annual_Rainfall"], 0.0)
fert_val = parse_float_safe(row["Fertilizer"], 0.0)
pest_val = parse_float_safe(row["Pesticide"], 0.0)

# Observed yield (optional)
observed_yield_val = None
if yield_col:
    observed_yield_val = parse_float_safe(row.get(yield_col, None), None)

# ---------- DISPLAY ----------
st.markdown("### Selected row values")
col1, col2 = st.columns([2,1])
with col1:
    st.markdown(f"**Crop:** `{crop_val}`")
    st.markdown(f"**State:** `{state_val}`")
    st.markdown(f"**Season:** `{season_val}`")
    st.markdown(f"**Crop Year:** `{crop_year_val}`")
    if yield_col:
        st.markdown(f"**Observed Yield ({yield_col}):** `{observed_yield_val}`")
    else:
        st.markdown(f"**Observed Yield:** `(not present in dataset)`")
with col2:
    st.markdown(f"**Area (ha):** `{area_val}`")
    st.markdown(f"**Production (tonnes):** `{production_val}`")
    st.markdown(f"**Annual Rainfall (mm):** `{rain_val}`")
    st.markdown(f"**Fertilizer (kg/ha):** `{fert_val}`")
    st.markdown(f"**Pesticide (kg/ha):** `{pest_val}`")

# ---------- MODEL INPUT PREVIEW ----------
input_data = {
    "Crop": crop_val,
    "Crop_Year": crop_year_val,
    "Season": season_val,
    "State": state_val,
    "Area": area_val,
    "Production": production_val,
    "Annual_Rainfall": rain_val,
    "Fertilizer": fert_val,
    "Pesticide": pest_val,
}
preview = input_data.copy()
if yield_col:
    preview["Observed_Yield"] = observed_yield_val

st.markdown("### Model Input (preview)")
st.table(pd.DataFrame([preview]).T.rename(columns={0: "Value"}))

# ---------- PREDICTION & VISUALS ----------
# Keep references to figures so we can embed them in a PDF later.
fig1 = fig2 = fig3 = fig4 = None

try:
    df_in = pd.DataFrame([input_data])

    # NOTE: pipeline may expect certain columns/order. If your pipeline requires specific columns,
    # ensure df_in has them (we assume earlier pipeline.predict(df_in) worked for you).
    pred_raw = pipeline.predict(df_in)
    pred = normalize_prediction(pred_raw)

    st.success(f"Predicted Yield: **{pred:.4f}**")
    st.markdown("---")

    # Observed vs Predicted bar
    fig1, ax1 = plt.subplots(figsize=(4,3))
    labels = ["Predicted"]
    values = [pred]
    if yield_col and (observed_yield_val is not None):
        labels.append("Observed")
        values.append(float(observed_yield_val))
    ax1.bar(labels, values, color=["#3b82f6", "#34d399"][:len(values)])
    ax1.set_ylabel("Yield")
    ax1.set_title("Predicted vs Observed Yield")
    for i, v in enumerate(values):
        ax1.text(i, v, f"{v:.2f}", ha="center", va="bottom")
    st.pyplot(fig1)
    plt.close(fig1)

    # Time series, scatter, histogram
    crop_df = df[df["Crop"] == crop_val].copy()
    crop_df["Crop_Year_num"] = pd.to_numeric(crop_df["Crop_Year"], errors="coerce")
    crop_df["Production_num"] = pd.to_numeric(crop_df["Production"], errors="coerce")
    ts_df = crop_df.dropna(subset=["Crop_Year_num", "Production_num"]).sort_values("Crop_Year_num")

    if len(ts_df) >= 2:
        fig2, ax2 = plt.subplots(figsize=(7,3.5))
        ax2.plot(ts_df["Crop_Year_num"], ts_df["Production_num"], marker="o", color="#0f172a")
        ax2.set_xlabel("Crop Year"); ax2.set_ylabel("Production (tonnes)")
        ax2.set_title(f"Production over Years — {crop_val}")
        st.pyplot(fig2); plt.close(fig2)
    else:
        st.info("Not enough rows for time-series (Crop_Year vs Production) for this crop.")

    scatter_df = crop_df.dropna(subset=["Area", "Production"]).copy()
    scatter_df["Area_num"] = pd.to_numeric(scatter_df["Area"], errors="coerce")
    scatter_df["Production_num"] = pd.to_numeric(scatter_df["Production"], errors="coerce")
    scatter_df = scatter_df.dropna(subset=["Area_num", "Production_num"])

    if len(scatter_df) >= 5:
        slope, intercept = safe_linear_fit(scatter_df["Area_num"].values, scatter_df["Production_num"].values)
        fig3, ax3 = plt.subplots(figsize=(6,4))
        ax3.scatter(scatter_df["Area_num"], scatter_df["Production_num"], alpha=0.7, color="#ef4444")
        if (slope is not None) and (intercept is not None):
            xs = np.linspace(scatter_df["Area_num"].min(), scatter_df["Area_num"].max(), 100)
            ax3.plot(xs, slope * xs + intercept, linestyle="--", color="#3b82f6")
            ax3.set_title(f"Area vs Production — trend slope {slope:.4f}")
        else:
            ax3.set_title("Area vs Production")
        ax3.set_xlabel("Area (ha)"); ax3.set_ylabel("Production (tonnes)")
        st.pyplot(fig3); plt.close(fig3)
    else:
        st.info("Not enough data for Area vs Production scatter (need ≥5 rows for this crop).")

    if yield_col:
        yield_vals = pd.to_numeric(crop_df.get(yield_col, pd.Series(dtype=float)), errors="coerce").dropna()
        if len(yield_vals) >= 2:
            fig4, ax4 = plt.subplots(figsize=(6,3))
            ax4.hist(yield_vals, bins=25, color="#10b981", alpha=0.8)
            ax4.set_title(f"Observed Yield Distribution for {crop_val} (column: {yield_col})")
            ax4.set_xlabel("Observed yield"); ax4.set_ylabel("Frequency")
            st.pyplot(fig4); plt.close(fig4)
        else:
            st.info("Not enough observed-yield values to render histogram for this crop.")

    if yield_col and (observed_yield_val is not None):
        diff = pred - float(observed_yield_val)
        pct = (diff / float(observed_yield_val) * 100) if observed_yield_val != 0 else None
        st.markdown("### Prediction vs Observed summary")
        st.write(f"- Observed ({yield_col}): {observed_yield_val:.4f}")
        st.write(f"- Predicted: {pred:.4f}")
        st.write(f"- Error (pred - obs): {diff:.4f}")
        if pct is not None:
            st.write(f"- Percentage error: {pct:.2f}%")

except Exception as e:
    st.error("Prediction or visualization failed.")
    st.exception(e)

# ---------- PDF REPORT GENERATION & DOWNLOAD ----------
# Utility: save figure to PNG if fig exists
def save_fig_if_exists(fig, filename):
    try:
        if fig is not None:
            fig.savefig(filename, dpi=150, bbox_inches="tight")
            return True
    except Exception:
        pass
    return False

# Create PDF from text + optional images
def create_pdf_report_bytes(
    crop_val, state_val, season_val, crop_year_val,
    area_val, production_val, rain_val, fert_val, pest_val,
    pred, observed_yield_val, yield_col,
    image_files
):
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Crop Yield Prediction Report", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", size=11)

    text_lines = [
        f"Crop: {crop_val}",
        f"State: {state_val}",
        f"Season: {season_val}",
        f"Crop Year: {crop_year_val}",
        "",
        f"Area (ha): {area_val}",
        f"Production (tonnes): {production_val}",
        f"Annual Rainfall (mm): {rain_val}",
        f"Fertilizer (kg/ha): {fert_val}",
        f"Pesticide (kg/ha): {pest_val}",
        "",
        f"Predicted Yield: {pred:.4f}"
    ]
    if yield_col and (observed_yield_val is not None):
        text_lines.append(f"Observed Yield ({yield_col}): {observed_yield_val:.4f}")

    for line in text_lines:
        pdf.cell(0, 7, line, ln=True)

    pdf.ln(6)
    # Add images (each on new page if too large)
    for image in image_files:
        if image and os.path.exists(image):
            try:
                pdf.add_page()
                # fit width to page margin: 190mm wide usable on A4
                pdf.image(image, x=10, w=190)
            except Exception:
                # if image can't be placed, skip gracefully
                pass

    return pdf.output(dest="S").encode("latin1")

# Prepare temporary filenames
tmp_images = {
    "pred_obs": "tmp_chart_pred_obs.png",
    "timeseries": "tmp_chart_timeseries.png",
    "scatter": "tmp_chart_scatter.png",
    "hist": "tmp_chart_hist.png"
}

# Save existing figs to files
saved_files = []
if save_fig_if_exists(fig1, tmp_images["pred_obs"]):
    saved_files.append(tmp_images["pred_obs"])
if save_fig_if_exists(fig2, tmp_images["timeseries"]):
    saved_files.append(tmp_images["timeseries"])
if save_fig_if_exists(fig3, tmp_images["scatter"]):
    saved_files.append(tmp_images["scatter"])
if save_fig_if_exists(fig4, tmp_images["hist"]):
    saved_files.append(tmp_images["hist"])

# Build PDF bytes
try:
    pdf_bytes = create_pdf_report_bytes(
        crop_val, state_val, season_val, crop_year_val,
        area_val, production_val, rain_val, fert_val, pest_val,
        pred if 'pred' in locals() else float("nan"),
        observed_yield_val, yield_col,
        saved_files
    )

    # Provide download button (Streamlit supports bytes directly)
    st.download_button(
        label="📥 Download Full Report (PDF)",
        data=pdf_bytes,
        file_name=f"crop_yield_report_{crop_val.replace(' ','_')}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error("Failed to build downloadable PDF.")
    st.exception(e)

# optional: cleanup temp image files
for f in saved_files:
    try:
        os.remove(f)
    except Exception:
        pass
