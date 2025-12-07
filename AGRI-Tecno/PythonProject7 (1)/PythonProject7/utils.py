import os
import shutil
import random
import matplotlib.pyplot as plt


def prepare_combined_dataset(src_root, dst_root, val_split=0.2):
    if os.path.exists(dst_root):
        print("Combined dataset already exists. Skipping creation.")
        return

    print("Preparing dataset...")
    os.makedirs(dst_root, exist_ok=True)
    os.makedirs(f"{dst_root}/train", exist_ok=True)
    os.makedirs(f"{dst_root}/val", exist_ok=True)

    folders = ["CyAUG-Dataset", "Orignal-Dataset"]

    for folder in folders:
        full_path = os.path.join(src_root, folder)

        for class_name in os.listdir(full_path):
            class_path = os.path.join(full_path, class_name)
            images = os.listdir(class_path)

            random.shuffle(images)
            split = int(len(images) * (1 - val_split))

            train_imgs = images[:split]
            val_imgs = images[split:]

            os.makedirs(f"{dst_root}/train/{class_name}", exist_ok=True)
            os.makedirs(f"{dst_root}/val/{class_name}", exist_ok=True)

            for img in train_imgs:
                shutil.copy(os.path.join(class_path, img),
                            f"{dst_root}/train/{class_name}/{img}")

            for img in val_imgs:
                shutil.copy(os.path.join(class_path, img),
                            f"{dst_root}/val/{class_name}/{img}")

    print("Dataset prepared ✔")


def plot_metrics(train_loss, val_loss, train_acc, val_acc):
    os.makedirs("checkpoints", exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(train_loss, label="Train Loss")
    plt.plot(val_loss, label="Validation Loss")
    plt.legend()
    plt.savefig("checkpoints/loss_curve.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(train_acc, label="Train Accuracy")
    plt.plot(val_acc, label="Validation Accuracy")
    plt.legend()
    plt.savefig("checkpoints/accuracy_curve.png")
    plt.close()

    print("Graphs saved ✔")
