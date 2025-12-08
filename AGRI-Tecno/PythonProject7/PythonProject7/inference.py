import torch
from torchvision import models, transforms
from PIL import Image
from model import SoilClassifier
# -------------------------
# IMPORTANT: Set correct num classes from your model
# -------------------------
NUM_CLASSES = 7  # CHANGE THIS TO MATCH YOUR TRAINED MODEL

# -------------------------
# 1. Create the model
# -------------------------

model = SoilClassifier(num_classes=NUM_CLASSES)
# -------------------------
# 2. Load state_dict safely
# -------------------------
raw_state = torch.load("checkpoints/best_model.pth", map_location="cpu")

# If saved inside {"model": state_dict}
if "model" in raw_state:
    raw_state = raw_state["model"]

# Remove "model." prefix
clean_state = {}
for key in raw_state.keys():
    new_key = key.replace("model.", "")
    clean_state[new_key] = raw_state[key]

# Load safely
model.load_state_dict(clean_state)
model.eval()

# -------------------------
# 3. Image Transform
# -------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def predict(img_path):
    img = Image.open(img_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
        _, pred = torch.max(output, 1)

    return pred.item()

# -------------------------
# 4. Run
# -------------------------
if __name__ == "__main__":
    img_path = input("Enter image path: ")
    result = predict(img_path)
    print("\nPredicted Class Index:", result)
