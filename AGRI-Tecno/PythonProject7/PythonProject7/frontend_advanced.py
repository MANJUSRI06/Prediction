import streamlit as st
import torch
from torchvision import models, transforms
from PIL import Image
from fpdf import FPDF
import time

# ---------------------------------------------
# CONFIG
# ---------------------------------------------

NUM_CLASSES = 5
class_names = ["Black Soil", "Red Soil", "Sandy Soil", "Clay Soil", "Alluvial Soil"]

soil_info = {
    "Black Soil": {
        "description": "Rich in minerals, retains moisture, ideal for cotton.",
        "fertilizer": "Nitrogen-rich fertilizers recommended."
    },
    "Red Soil": {
        "description": "Poor in nitrogen, rich in iron, best for groundnut and wheat.",
        "fertilizer": "Use phosphate and potash fertilizers."
    },
    "Sandy Soil": {
        "description": "Drains quickly, low water retention.",
        "fertilizer": "Organic compost recommended."
    },
    "Clay Soil": {
        "description": "Dense and retains water, suitable for rice.",
        "fertilizer": "Balanced NPK fertilizers recommended."
    },
    "Alluvial Soil": {
        "description": "Fertile soil found in river plains, ideal for wheat and rice.",
        "fertilizer": "NPK + compost recommended."
    }
}

# ---------------------------------------------
# LOAD MODEL
# ---------------------------------------------

@st.cache_resource
def load_model():
    checkpoint = torch.load("models/best_model.pth", map_location="cpu")

    if "model" in checkpoint:
        checkpoint = checkpoint["model"]

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, NUM_CLASSES)

    model_state = model.state_dict()
    new_state = {}

    for key, value in checkpoint.items():
        if key in model_state and model_state[key].shape == value.shape:
            new_state[key] = value
        else:
            print(f"Skipping layer (shape mismatch): {key}")

    model_state.update(new_state)
    model.load_state_dict(model_state, strict=False)
    model.eval()
    return model


model = load_model()

# ---------------------------------------------
# IMAGE TRANSFORM
# ---------------------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ---------------------------------------------
# CUSTOM CSS
# ---------------------------------------------

st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #e0f7fa, #b2dfdb);
}
.title {
    font-size: 42px;
    font-weight: 800;
    color: #2E7D32;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #444;
    margin-bottom: 30px;
}
.prediction-card {
    padding: 20px;
    border-radius: 15px;
    background: #E8F5E9;
    text-align: center;
    border: 2px solid #4CAF50;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# HEADER
# ---------------------------------------------

st.markdown('<div class="title">🌱 Advanced Soil Classification</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload one or multiple images to classify soil type using AI</div>', unsafe_allow_html=True)

# ---------------------------------------------
# MANUAL DROPDOWN
# ---------------------------------------------

manual_soil = st.selectbox("Or select soil type manually", ["Select"] + class_names)
if manual_soil != "Select":
    st.info(f"Description: {soil_info[manual_soil]['description']}\n\n"
            f"Fertilizer: {soil_info[manual_soil]['fertilizer']}")

# ---------------------------------------------
# IMAGE UPLOAD
# ---------------------------------------------

uploaded_files = st.file_uploader("📁 Upload Soil Image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
camera_image = st.camera_input("📸 Take a Photo")

images = []
if uploaded_files:
    for f in uploaded_files:
        images.append(Image.open(f).convert("RGB"))
elif camera_image:
    images.append(Image.open(camera_image).convert("RGB"))

# ---------------------------------------------
# PREDICTION
# ---------------------------------------------

predictions = []

if images:
    with st.spinner("🧠 Classifying images..."):
        for img in images:
            st.image(img, width=280)

            img_tensor = transform(img).unsqueeze(0)

            with torch.no_grad():
                output = model(img_tensor)
                _, pred = torch.max(output, 1)
                predicted_class = class_names[pred.item()]
                predictions.append(predicted_class)

            st.markdown(f"""
            <div class="prediction-card">
                <h2>Predicted Soil Type</h2>
                <h1 style="color:#1B5E20">{predicted_class}</h1>
                <p>{soil_info[predicted_class]['description']}</p>
                <p><b>Fertilizer:</b> {soil_info[predicted_class]['fertilizer']}</p>
            </div>
            """, unsafe_allow_html=True)

            time.sleep(0.5)

# ---------------------------------------------
# PDF REPORT
# ---------------------------------------------

if predictions:
    pdf_btn = st.button("📄 Download Report as PDF")

    if pdf_btn:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, "Soil Classification Report", ln=True, align="C")

        pdf.ln(10)

        for idx, pred in enumerate(predictions):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Image {idx+1}: {pred}", ln=True)

            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(
                0,
                8,
                f"Description: {soil_info[pred]['description']}\n"
                f"Fertilizer Recommendation: {soil_info[pred]['fertilizer']}\n",
            )
            pdf.ln(5)

        # FIX: Correct encoding
        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="soil_report.pdf",
            mime="application/pdf"
        )
