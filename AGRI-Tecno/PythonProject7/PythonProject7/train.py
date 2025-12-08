import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
import os
from utils import prepare_combined_dataset, plot_metrics
from model import SoilClassifier
from tqdm import tqdm

DATA_DIR = "dataset"
COMBINED_DIR = "combined_dataset"
CHECKPOINT_DIR = "checkpoints"


def train_model():
    # Prepare dataset
    prepare_combined_dataset(DATA_DIR, COMBINED_DIR)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    train_dataset = datasets.ImageFolder(os.path.join(COMBINED_DIR, "train"), transform=transform)
    val_dataset = datasets.ImageFolder(os.path.join(COMBINED_DIR, "val"), transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = SoilClassifier(num_classes=len(train_dataset.classes)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    best_accuracy = 0
    train_losses, val_losses, train_acc, val_acc = [], [], [], []

    for epoch in range(50):
        print(f"\nEPOCH {epoch + 1}/10")

        model.train()
        running_loss, correct, total = 0, 0, 0

        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        train_loss = running_loss / len(train_loader)
        train_accuracy = correct / total

        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_accuracy:.4f}")

        model.eval()
        v_loss, v_correct, v_total = 0, 0, 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)

                loss = criterion(outputs, labels)
                v_loss += loss.item()

                _, predicted = outputs.max(1)
                v_total += labels.size(0)
                v_correct += predicted.eq(labels).sum().item()

        val_loss = v_loss / len(val_loader)
        val_accuracy = v_correct / v_total

        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_accuracy:.4f}")

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_acc.append(train_accuracy)
        val_acc.append(val_accuracy)

        # Save best model
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            os.makedirs(CHECKPOINT_DIR, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(CHECKPOINT_DIR, "best_model.pth"))
            print("Model Saved ✔")

    # Save graphs
    plot_metrics(train_losses, val_losses, train_acc, val_acc)
    torch.save(model.state_dict(), "soil_model.pth")
    print("Final model saved as soil_model.pth ✔")


if __name__ == "__main__":
    train_model()
