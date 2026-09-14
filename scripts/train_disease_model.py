r"""Train a real crop-disease classifier from an ImageFolder dataset.

Example:
  .\.venv\Scripts\python.exe scripts\train_disease_model.py --data data\plant_disease --epochs 12

Expected folders:
  data/plant_disease/train/Tomato___Early_Blight/*.jpg
  data/plant_disease/train/Tomato___Healthy/*.jpg
  data/plant_disease/val/Tomato___Early_Blight/*.jpg
  data/plant_disease/val/Tomato___Healthy/*.jpg
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train KrishiMitr's plant-disease model.")
    parser.add_argument("--data", type=Path, required=True, help="Dataset root containing train/ and val/.")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--output", type=Path, default=Path("weights/efficientnet_leaf_disease.pt"))
    parser.add_argument(
        "--from-scratch", action="store_true",
        help="Do not download ImageNet weights. This is much slower and less accurate than transfer learning.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Keep model-download cache inside the project. This avoids depending on
    # permissions for the user's Windows home cache folder.
    os.environ.setdefault("TORCH_HOME", str(Path("weights") / ".torch-cache"))
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader
        from torchvision import datasets, models, transforms
    except ImportError as exc:
        raise SystemExit("Install AI dependencies first: pip install -r requirements-ai.txt") from exc

    train_path, val_path = args.data / "train", args.data / "val"
    if not train_path.is_dir() or not val_path.is_dir():
        raise SystemExit("Dataset must contain both train/ and val/ class folders. See TRAINING_GUIDE.md.")

    train_transform = transforms.Compose([
        transforms.Resize((256, 256)), transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(), transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.12),
        transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)), transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    train_data = datasets.ImageFolder(train_path, transform=train_transform)
    val_data = datasets.ImageFolder(val_path, transform=val_transform)
    if train_data.classes != val_data.classes or len(train_data.classes) < 2:
        raise SystemExit("train/ and val/ must have the same two or more class folders.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loaders = {
        "train": DataLoader(train_data, batch_size=args.batch_size, shuffle=True, num_workers=0),
        "val": DataLoader(val_data, batch_size=args.batch_size, shuffle=False, num_workers=0),
    }
    try:
        pretrained_weights = None if args.from_scratch else models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=pretrained_weights)
    except Exception as exc:
        if args.from_scratch:
            raise
        raise SystemExit(
            "Could not download the pre-trained EfficientNet weights. Download is blocked or unavailable. "
            "Do not train from scratch unless necessary; it is slower and less accurate. "
            "See TRAINING_GUIDE.md for the browser-download workaround."
        ) from exc
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(train_data.classes))
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()
    best_accuracy = -1.0
    args.output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_correct = train_total = 0
        for images, labels in loaders["train"]:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = loss_fn(logits, labels)
            loss.backward()
            optimizer.step()
            train_correct += (logits.argmax(1) == labels).sum().item()
            train_total += labels.size(0)

        model.eval()
        val_correct = val_total = 0
        with torch.no_grad():
            for images, labels in loaders["val"]:
                logits = model(images.to(device))
                val_correct += (logits.argmax(1).cpu() == labels).sum().item()
                val_total += labels.size(0)
        train_accuracy = train_correct / max(train_total, 1)
        val_accuracy = val_correct / max(val_total, 1)
        print(f"Epoch {epoch}/{args.epochs}: train={train_accuracy:.1%}, validation={val_accuracy:.1%}")
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save({"state_dict": model.state_dict(), "class_labels": train_data.classes}, args.output)
            print(f"Saved best model to {args.output} ({best_accuracy:.1%})")


if __name__ == "__main__":
    main()
