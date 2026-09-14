r"""Split labelled disease-image folders into KrishiMitr train/validation data.

Example:
  .\.venv\Scripts\python.exe scripts\prepare_dataset.py --source D:\Downloads\PlantVillage --output data\plant_disease
"""
from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create train/val folders from labelled image folders.")
    parser.add_argument("--source", type=Path, required=True, help="Folder whose direct subfolders are disease labels.")
    parser.add_argument("--output", type=Path, default=Path("data/plant_disease"))
    parser.add_argument("--validation-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not args.source.is_dir() or not 0 < args.validation_ratio < 0.5:
        raise SystemExit("--source must exist and --validation-ratio must be between 0 and 0.5.")
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"Output folder is not empty: {args.output}. Use a new empty folder.")

    random.seed(args.seed)
    class_dirs = [path for path in args.source.iterdir() if path.is_dir()]
    if len(class_dirs) < 2:
        raise SystemExit("Source needs at least two labelled class folders.")

    for class_dir in class_dirs:
        images = [path for path in class_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES]
        if len(images) < 10:
            print(f"Skipping {class_dir.name}: only {len(images)} images (need at least 10).")
            continue
        random.shuffle(images)
        val_count = max(1, round(len(images) * args.validation_ratio))
        for split, split_images in (("val", images[:val_count]), ("train", images[val_count:])):
            destination = args.output / split / class_dir.name
            destination.mkdir(parents=True, exist_ok=True)
            for image in split_images:
                shutil.copy2(image, destination / image.name)
        print(f"{class_dir.name}: {len(images) - val_count} train, {val_count} validation")


if __name__ == "__main__":
    main()
