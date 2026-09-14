"""
EfficientNet-based crop disease classifier.

In production this module would load real trained weights, e.g.:

    import torch
    from torchvision.models import efficientnet_b0
    model = efficientnet_b0(weights=None)
    model.load_state_dict(torch.load("weights/efficientnet_leaf_disease.pt"))
    model.eval()

The shipped checkpoint is loaded locally whenever it is present. A small,
deterministic fallback preserves the same ``predict(image_array)`` interface
when a developer runs the app without the optional model artefact.
"""
import hashlib
from pathlib import Path
from typing import Tuple

import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)
WEIGHTS_PATH = Path(__file__).resolve().parents[2] / "weights" / "efficientnet_leaf_disease.pt"

# Class labels this "model" was mock-trained on (mirrors PlantVillage-style datasets)
CLASS_LABELS = [
    "Healthy",
    "Tomato___Early_Blight",
    "Tomato___Late_Blight",
    "Potato___Early_Blight",
    "Potato___Late_Blight",
    "Wheat___Leaf_Rust",
    "Wheat___Powdery_Mildew",
    "Cotton___Bacterial_Blight",
    "Rice___Bacterial_Leaf_Blight",
    "Rice___Brown_Spot",
    "Maize___Common_Rust",
]

REMEDIES = {
    "Healthy": {
        "hi": "आपकी फसल स्वस्थ दिखाई दे रही है। नियमित निगरानी जारी रखें और संतुलित उर्वरक का उपयोग करें।",
        "en": "Your crop looks healthy. Continue regular monitoring and balanced fertilization.",
    },
    "Tomato___Early_Blight": {
        "hi": "प्रभावित पत्तियों को हटा दें। मैंकोज़ेब या क्लोरोथैलोनिल आधारित फफूंदनाशक का छिड़काव करें। फसल चक्रण अपनाएं।",
        "en": "Remove affected leaves. Spray a mancozeb or chlorothalonil-based fungicide. Practice crop rotation.",
    },
    "Tomato___Late_Blight": {
        "hi": "तुरंत मेटालैक्सिल/कॉपर ऑक्सीक्लोराइड का छिड़काव करें। खेत में जल निकासी सुधारें, बारिश के मौसम में सतर्क रहें।",
        "en": "Spray metalaxyl or copper oxychloride immediately. Improve field drainage and monitor closely during wet weather.",
    },
    "Potato___Early_Blight": {
        "hi": "मैंकोज़ेब आधारित फफूंदनाशक का प्रयोग करें और खेत में उचित दूरी बनाए रखें।",
        "en": "Use a mancozeb-based fungicide and ensure proper plant spacing for airflow.",
    },
    "Potato___Late_Blight": {
        "hi": "साइमोक्सानिल+मैंकोज़ेब मिश्रण का छिड़काव करें। संक्रमित पौधों को तुरंत नष्ट करें।",
        "en": "Spray a cymoxanil + mancozeb mixture. Destroy infected plants immediately to prevent spread.",
    },
    "Wheat___Leaf_Rust": {
        "hi": "प्रोपिकोनाज़ोल आधारित फफूंदनाशक का छिड़काव करें। रोग प्रतिरोधी किस्मों का उपयोग अगली बुवाई में करें।",
        "en": "Spray a propiconazole-based fungicide. Use rust-resistant wheat varieties in the next sowing.",
    },
    "Wheat___Powdery_Mildew": {
        "hi": "सल्फर आधारित फफूंदनाशक का छिड़काव करें और खेत में हवा का संचार बनाए रखें।",
        "en": "Apply a sulfur-based fungicide and maintain good airflow in the field.",
    },
    "Cotton___Bacterial_Blight": {
        "hi": "कॉपर ऑक्सीक्लोराइड का छिड़काव करें। बीज उपचार अगली बुवाई से पहले अवश्य करें।",
        "en": "Spray copper oxychloride. Ensure seed treatment before the next sowing cycle.",
    },
    "Rice___Bacterial_Leaf_Blight": {
        "hi": "स्ट्रेप्टोसाइक्लिन + कॉपर ऑक्सीक्लोराइड मिश्रण का छिड़काव करें। खेत में अतिरिक्त पानी न भरने दें।",
        "en": "Spray a streptocycline + copper oxychloride mix. Avoid excess standing water in the field.",
    },
    "Rice___Brown_Spot": {
        "hi": "संतुलित पोटाश उर्वरक दें और प्रोपिकोनाज़ोल का छिड़काव करें।",
        "en": "Apply balanced potash fertilizer and spray propiconazole.",
    },
    "Maize___Common_Rust": {
        "hi": "प्रतिरोधी किस्में लगाएं और आवश्यकता होने पर फफूंदनाशक का प्रयोग करें।",
        "en": "Plant resistant hybrid varieties and apply fungicide if infestation is severe.",
    },
}


def remedy_for_label(label: str) -> dict[str, str] | None:
    """Return the treatment guidance for a model label, ignoring label style.

    PlantVillage labels in a trained checkpoint use mixed case such as
    ``Tomato___Late_blight`` while the original demo table used
    ``Tomato___Late_Blight``.  A direct dictionary lookup therefore made a
    successful prediction appear to have no guidance.  Normalising both sides
    keeps the advice tied to the detected disease rather than to presentation
    details in the dataset label.
    """
    def normalise(value: str) -> str:
        return " ".join(value.replace("___", " ").replace("_", " ").lower().split())

    target = normalise(label)
    for remedy_label, remedy in REMEDIES.items():
        if normalise(remedy_label) == target:
            return remedy
    return None

CROP_FROM_LABEL = {label: label.split("___")[0] if "___" in label else "Unknown" for label in CLASS_LABELS}


class DiseaseClassifierModel:
    """
    Mock EfficientNet-B0 wrapper.

    `predict()` deterministically derives a "prediction" from the image's
    pixel statistics (mean color channels + a content hash) so that the
    same image always yields the same result, and different images plausibly
    yield different results — mimicking a trained CNN's behavior without
    requiring real model weights or a GPU.
    """

    def __init__(self):
        self.input_size = (224, 224)  # standard EfficientNet-B0 input
        self.class_labels = CLASS_LABELS
        logger.info("Mock EfficientNet-B0 disease classifier initialized (in-memory heuristic mode).")

    def predict(self, preprocessed_image: np.ndarray) -> Tuple[str, float]:
        """
        Args:
            preprocessed_image: np.ndarray of shape (224, 224, 3), float32, normalized [0, 1]
        Returns:
            (predicted_label, confidence_score)
        """
        if preprocessed_image.shape[:2] != self.input_size:
            raise ValueError(f"Expected input size {self.input_size}, got {preprocessed_image.shape[:2]}")

        # Derive a stable "feature fingerprint" from mean channel intensities + a content hash.
        mean_r, mean_g, mean_b = preprocessed_image.mean(axis=(0, 1))
        image_hash = hashlib.sha256(preprocessed_image.tobytes()).hexdigest()
        hash_int = int(image_hash[:8], 16)

        # Heuristic: healthy leaves are predominantly green (high G relative to R/B).
        greenness = mean_g - ((mean_r + mean_b) / 2.0)

        if greenness > 0.12:
            label = "Healthy"
            confidence = min(0.99, 0.80 + greenness)
        else:
            # Use the hash to deterministically pick a disease class (excluding "Healthy")
            disease_labels = [l for l in self.class_labels if l != "Healthy"]
            label = disease_labels[hash_int % len(disease_labels)]
            # Lower greenness -> model is "more confident" it found a lesion pattern
            confidence = min(0.97, 0.55 + (0.12 - greenness) * 2.0)
            confidence = max(0.55, confidence)

        logger.info(f"Disease classifier prediction: {label} (confidence={confidence:.2f})")
        return label, float(confidence)


class TrainedDiseaseClassifierModel:
    """EfficientNet inference wrapper for the model produced by the trainer."""

    def __init__(self, weights_path: Path):
        import torch
        from torch import nn
        from torchvision import models

        checkpoint = torch.load(weights_path, map_location="cpu", weights_only=True)
        self.class_labels = checkpoint["class_labels"]
        self.model = models.efficientnet_b0(weights=None)
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, len(self.class_labels))
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
        self.torch = torch
        logger.info("Loaded trained disease classifier with %d classes from %s", len(self.class_labels), weights_path)

    def predict(self, preprocessed_image: np.ndarray) -> Tuple[str, float]:
        if preprocessed_image.shape[:2] != (224, 224):
            raise ValueError(f"Expected 224x224 input, got {preprocessed_image.shape[:2]}")
        # The trainer uses ImageNet normalisation; OpenCV preprocessing already
        # provides RGB pixels in [0, 1].
        normalized = (preprocessed_image - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
        tensor = self.torch.from_numpy(normalized.transpose(2, 0, 1)).unsqueeze(0)
        with self.torch.no_grad():
            probabilities = self.torch.softmax(self.model(tensor), dim=1)[0]
        index = int(probabilities.argmax().item())
        return self.class_labels[index], float(probabilities[index].item())

    def predict_for_crop(self, preprocessed_image: np.ndarray, crop_prefix: str) -> tuple[str, float, float]:
        """Choose a disease class conditioned on the farmer-confirmed crop.

        A PlantVillage classifier is trained across several crops, so visually
        similar lesions can make its global winner a different crop. Once a
        farmer has explicitly selected a crop, compare only classes of that
        crop and report the conditional confidence. ``crop_probability`` is
        kept separately so a completely unrelated image is still rejected.
        """
        if preprocessed_image.shape[:2] != (224, 224):
            raise ValueError(f"Expected 224x224 input, got {preprocessed_image.shape[:2]}")
        normalized = (preprocessed_image - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
        tensor = self.torch.from_numpy(normalized.transpose(2, 0, 1)).unsqueeze(0)
        with self.torch.no_grad():
            probabilities = self.torch.softmax(self.model(tensor), dim=1)[0]
        indexes = [i for i, label in enumerate(self.class_labels) if label.startswith(crop_prefix)]
        if not indexes:
            raise ValueError(f"No trained classes exist for crop prefix {crop_prefix!r}")
        crop_probability = float(probabilities[indexes].sum().item())
        best_index = max(indexes, key=lambda index: float(probabilities[index].item()))
        conditional_confidence = float(probabilities[best_index].item()) / max(crop_probability, 1e-8)
        return self.class_labels[best_index], conditional_confidence, crop_probability


# Singleton instance (mirrors how a real model would be loaded once at startup)
_model_instance: DiseaseClassifierModel | TrainedDiseaseClassifierModel | None = None


def get_disease_model() -> DiseaseClassifierModel | TrainedDiseaseClassifierModel:
    global _model_instance
    if _model_instance is None:
        if WEIGHTS_PATH.is_file():
            try:
                _model_instance = TrainedDiseaseClassifierModel(WEIGHTS_PATH)
            except (ImportError, KeyError, RuntimeError, ValueError) as exc:
                logger.warning("Could not load trained model (%s); using demo classifier.", exc)
                _model_instance = DiseaseClassifierModel()
        else:
            _model_instance = DiseaseClassifierModel()
    return _model_instance
