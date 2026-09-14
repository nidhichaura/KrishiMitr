# Real Disease Model: Beginner Guide

The current app has a demo classifier. This guide replaces it with a real model.

## 1. Get a labelled dataset

Use a trusted disease-photo dataset such as PlantVillage as a starting point. Add Indian field photos later because real farm lighting/backgrounds differ from laboratory images.

Every image must already be in the folder for its true class. Keep the source
dataset unchanged, then run this one command to make the training folders:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_dataset.py --source D:\Downloads\PlantVillage --output data\plant_disease
```

The script automatically puts 80% into training and 20% into validation. Its
output uses this format:

```
data/plant_disease/
  train/
    Cotton___Bacterial_Blight/
    Cotton___Healthy/
    Rice___Brown_Spot/
    Rice___Healthy/
    Tomato___Early_Blight/
    Tomato___Healthy/
  val/
    Cotton___Bacterial_Blight/
    Cotton___Healthy/
    Rice___Brown_Spot/
    Rice___Healthy/
    Tomato___Early_Blight/
    Tomato___Healthy/
```

Never put copies of the same photo in both folders.

## 2. Install the AI libraries

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
```

## 3. Train

```powershell
.\.venv\Scripts\python.exe scripts\train_disease_model.py --data data\plant_disease --epochs 12
```

### If it says pre-trained weights cannot download

Open this official PyTorch file in your browser, let it download, then move it
to this exact project folder:

```text
weights/.torch-cache/hub/checkpoints/efficientnet_b0_rwightman-7f5810bc.pth
```

Official download: https://download.pytorch.org/models/efficientnet_b0_rwightman-7f5810bc.pth

Then run the training command again. This model begins with ImageNet knowledge,
which is much better than learning all 38 classes from zero on a CPU.

The best model is saved at `weights/efficientnet_leaf_disease.pt`.

## 4. Start the app

The application detects this file automatically on startup and switches from
the demo classifier to the trained EfficientNet model. Restart the backend
after training. The folder/class names saved by the training script become the
labels returned to WhatsApp.

Before going live, add an approved farmer-safe remedy for every disease label
to `app/ml_models/disease_classifier.py`.

## 5. Test before trusting it

Test at least 20 new field photos not used in training: healthy and diseased leaves, different lighting, and non-leaf photos. Check each predicted label with an agriculture expert. Do not deploy treatment recommendations from accuracy alone.
