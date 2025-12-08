import torch
from PIL import Image
from torchvision import transforms
from model import SoilClassifier

# --------- SET NUMBER OF CLASSES ----------
NUM_CLASSES = 7   # Change this to match your dataset folders

# --------- LOAD MODEL ----------
model = SoilClassifier(num_classes=NUM_CLASSES)

state = torch.load("checkpoints/best_model.pth", map_location="cpu")

if "model" in state:
    state = state["model"]

clean_state = {k.replace("model.", ""): v for k, v in state.items()}
model.load_state_dict(clean_state, strict=False)
model.eval()

# --------- IMAGE TRANSFORM ----------
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

# --------- RUN ----------
if __name__ == "__main__":
    img = input("Enter image path: ")
    print("\nPredicted Class:", predict(img))
