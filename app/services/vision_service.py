"""Computer Vision Layer: OpenCV preprocessing + EfficientNet inference."""
import cv2
import numpy as np
from pathlib import Path

from app.ml_models.disease_classifier import get_disease_model, REMEDIES, CROP_FROM_LABEL, remedy_for_label
from app.models.schemas import DiseaseDetectionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

TARGET_SIZE = (224, 224)
# The trained classifier contains only leaf-disease classes; it cannot label
# something as "not a leaf" by itself.  Reject low-confidence predictions
# instead of forcing a potentially harmful disease label on an out-of-domain
# image.  Internal validation leaves score substantially above this threshold.
MIN_DISEASE_CONFIDENCE = 0.90
# Minimum total probability assigned to the farmer-selected crop before we
# condition the disease decision on that crop. This preserves the rejection
# path for unrelated images while allowing visually similar crop diseases to
# be compared fairly within the farmer-confirmed crop.
MIN_SELECTED_CROP_PROBABILITY = 0.12
_IMAGENET_WEIGHTS = Path(__file__).resolve().parents[2] / "weights" / ".torch-cache" / "hub" / "checkpoints" / "efficientnet_b0_rwightman-7f5810bc.pth"
_NON_LEAF_LABELS = {
    "desk", "dining table", "pool table", "table lamp", "barber chair",
    "folding chair", "rocking chair", "laptop", "desktop computer", "monitor",
    "computer keyboard", "typewriter keyboard", "cellular telephone", "dial telephone",
    "pay-phone", "remote control", "bookcase", "bookshop", "notebook", "comic book",
    "book jacket", "stone wall", "wall clock", "screen", "window screen", "wallet",
}
_general_image_model = None

# The shipped PlantVillage model only contains these crop groups. A requested
# crop must match the model output; this prevents a random photo/table from
# being presented as a disease of an unrelated crop.
_MODEL_CROP_PREFIXES = {
    "tomato": "Tomato", "potato": "Potato", "maize": "Corn_(maize)",
    "soybean": "Soybean", "apple": "Apple", "grape": "Grape",
    "orange": "Orange", "peach": "Peach", "bell pepper": "Pepper,_bell",
    "cherry": "Cherry_(including_sour)", "blueberry": "Blueberry",
    "strawberry": "Strawberry", "raspberry": "Raspberry", "squash": "Squash",
}

_PUNJABI_REMEDIES = {
    "Healthy": "ਫ਼ਸਲ ਸਿਹਤਮੰਦ ਲੱਗਦੀ ਹੈ। ਨਿਯਮਤ ਨਿਗਰਾਨੀ ਅਤੇ ਸੰਤੁਲਿਤ ਖਾਦ ਜਾਰੀ ਰੱਖੋ।",
    "Tomato___Early_blight": "ਪ੍ਰਭਾਵਿਤ ਪੱਤੇ ਹਟਾਓ। ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਨਾਲ ਮੈਂਕੋਜ਼ੇਬ ਜਾਂ ਕਲੋਰੋਥੈਲੋਨਿਲ ਆਧਾਰਿਤ ਫਫੂੰਦਨਾਸ਼ਕ ਵਰਤੋ ਅਤੇ ਫ਼ਸਲ ਚੱਕਰ ਅਪਣਾਓ।",
    "Tomato___Late_blight": "ਖੇਤ ਵਿੱਚ ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਸੁਧਾਰੋ ਅਤੇ ਗਿੱਲੇ ਮੌਸਮ ਵਿੱਚ ਫ਼ਸਲ ਨੂੰ ਧਿਆਨ ਨਾਲ ਦੇਖੋ। ਦਵਾਈ ਲਈ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਲਓ।",
    "Potato___Early_blight": "ਪ੍ਰਭਾਵਿਤ ਪੱਤੇ ਹਟਾਓ ਅਤੇ ਹਵਾ ਦੀ ਆਵਾਜਾਈ ਲਈ ਢੁੱਕਵਾਂ ਫ਼ਾਸਲਾ ਰੱਖੋ। ਦਵਾਈ ਲਈ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਗੱਲ ਕਰੋ।",
    "Potato___Late_blight": "ਸੰਕਰਮਿਤ ਪੌਦਿਆਂ ਨੂੰ ਵੱਖ ਕਰੋ, ਖੇਤ ਵਿੱਚ ਪਾਣੀ ਨਾ ਖੜ੍ਹਨ ਦਿਓ ਅਤੇ ਤੁਰੰਤ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਲਓ।",
    "Wheat___Leaf_Rust": "ਸੰਕਰਮਣ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ ਅਤੇ ਅਗਲੀ ਬਿਜਾਈ ਲਈ ਰੋਗ-ਰੋਧੀ ਕਿਸਮ ਚੁਣੋ। ਉਚਿਤ ਦਵਾਈ ਲਈ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਪੁੱਛੋ।",
    "Wheat___Powdery_Mildew": "ਖੇਤ ਵਿੱਚ ਹਵਾ ਦੀ ਆਵਾਜਾਈ ਬਣਾਈ ਰੱਖੋ ਅਤੇ ਉਚਿਤ ਇਲਾਜ ਲਈ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
    "Cotton___Bacterial_Blight": "ਪ੍ਰਭਾਵਿਤ ਪੱਤਿਆਂ ਨੂੰ ਹਟਾਓ ਅਤੇ ਅਗਲੀ ਬਿਜਾਈ ਤੋਂ ਪਹਿਲਾਂ ਬੀਜ ਇਲਾਜ ਬਾਰੇ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
    "Rice___Bacterial_Leaf_Blight": "ਖੇਤ ਵਿੱਚ ਵੱਧ ਪਾਣੀ ਖੜ੍ਹਾ ਨਾ ਰਹਿਣ ਦਿਓ ਅਤੇ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਤੋਂ ਇਲਾਜ ਦੀ ਸਲਾਹ ਲਓ।",
    "Rice___Brown_Spot": "ਸੰਤੁਲਿਤ ਪੋਟਾਸ਼ ਖਾਦ ਦਿਓ ਅਤੇ ਇਲਾਜ ਲਈ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
    "Maize___Common_Rust": "ਰੋਗ-ਰੋਧੀ ਹਾਈਬ੍ਰਿਡ ਚੁਣੋ ਅਤੇ ਹਮਲਾ ਗੰਭੀਰ ਹੋਵੇ ਤਾਂ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਨਾਲ ਇਲਾਜ ਕਰੋ।",
}


class InvalidLeafPhotoError(ValueError):
    """Raised when an image is too poor or unlikely to contain a crop leaf."""


class CropMismatchPhotoError(InvalidLeafPhotoError):
    """Raised when the pictured leaf does not match the named crop."""


class UnsupportedDiseaseCropError(InvalidLeafPhotoError):
    """Raised when a crop has no disease classes in the local model."""


class MissingDiseaseCropError(InvalidLeafPhotoError):
    """Raised when a disease-only model is asked to identify an unknown crop."""


def _reject_known_non_leaf_objects(image: np.ndarray) -> None:
    """Use ImageNet's general object model to reject obvious objects first.

    The disease model has only leaf classes.  This separate model knows common
    objects such as tables, desks, phones, books and keyboards, so it can stop
    them before the disease-only classifier is allowed to make a prediction.
    """
    global _general_image_model
    if not _IMAGENET_WEIGHTS.is_file():
        logger.warning("General image safety model is unavailable at %s", _IMAGENET_WEIGHTS)
        return
    if _general_image_model is None:
        import torch
        from torchvision import models

        weights = models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=None)
        model.load_state_dict(torch.load(_IMAGENET_WEIGHTS, map_location="cpu", weights_only=True))
        model.eval()
        _general_image_model = (model, torch, weights.meta["categories"])

    model, torch, labels = _general_image_model
    rgb = cv2.cvtColor(cv2.resize(image, (224, 224)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    normalized = (rgb - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
    tensor = torch.from_numpy(normalized.transpose(2, 0, 1)).unsqueeze(0)
    with torch.no_grad():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
    index = int(probabilities.argmax().item())
    label, confidence = labels[index], float(probabilities[index].item())
    logger.info("General image check: label=%s confidence=%.3f", label, confidence)
    if label in _NON_LEAF_LABELS and confidence >= 0.25:
        raise InvalidLeafPhotoError(f"Image appears to be a non-leaf object ({label}).")


def warm_image_safety_model() -> None:
    """Load the general-object gate during startup, not during a webhook."""
    if not _IMAGENET_WEIGHTS.is_file():
        return
    # A single harmless image triggers lazy model construction without a
    # network call; errors remain non-fatal for the rest of the service.
    try:
        _reject_known_non_leaf_objects(np.zeros((224, 224, 3), dtype=np.uint8))
    except InvalidLeafPhotoError:
        pass


def _decode_image(image_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidLeafPhotoError("The image could not be decoded.")
    return image


def validate_leaf_photo(image: np.ndarray) -> None:
    """Reject clearly unusable or non-vegetation images before classification.

    This is a conservative quality gate, not a replacement for a trained leaf
    detector. It catches common mistakes such as a wall/table, a screenshot,
    or an extremely blurred image and asks for a better photograph.
    """
    height, width = image.shape[:2]
    if min(height, width) < 80:
        raise InvalidLeafPhotoError("Image is too small for disease analysis.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if cv2.Laplacian(gray, cv2.CV_64F).var() < 18:
        raise InvalidLeafPhotoError("Image is too blurred for disease analysis.")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)
    # Green, yellow and brown plant tissue.  Diseased leaves are often yellow
    # or brown, so validating only green pixels would reject the photos we need.
    plant_colours = (((hue >= 8) & (hue <= 95)) & (saturation >= 45) & (value >= 30) & (value <= 245)).astype(np.uint8)
    plant_coverage = float(plant_colours.mean())
    if plant_coverage < 0.12:
        raise InvalidLeafPhotoError("Image does not contain enough visible leaf tissue.")
    # Do not reject a high-coverage image: a close-up of a single tomato leaf
    # commonly fills almost the entire frame, and is exactly the image a leaf
    # disease classifier needs. The connected-component check below still
    # rejects landscapes and visually fragmented/non-leaf scenes.

    # A disease photo should show one principal leaf, not a landscape, crop
    # field, screenshot, or a collection of unrelated colourful objects.
    cleaned = cv2.morphologyEx(plant_colours, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
    component_areas = stats[1:, cv2.CC_STAT_AREA] if count > 1 else np.array([])
    significant = component_areas[component_areas >= image.shape[0] * image.shape[1] * 0.01]
    if not len(significant) or significant.max() / max(significant.sum(), 1) < 0.60:
        raise InvalidLeafPhotoError("Image does not show one clear primary leaf.")


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Decode raw image bytes and preprocess for CNN inference:
      1. Decode via OpenCV
      2. Resize to model input size (224x224 for EfficientNet-B0)
      3. Denoise (mild Gaussian blur) to reduce camera-sensor noise
      4. Convert BGR -> RGB (OpenCV loads as BGR by default)
      5. Normalize pixel values to [0, 1] float32
    """
    image = _decode_image(image_bytes)
    _reject_known_non_leaf_objects(image)
    validate_leaf_photo(image)

    resized = cv2.resize(image, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    denoised = cv2.GaussianBlur(resized, (3, 3), sigmaX=0)
    rgb_image = cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)
    normalized = rgb_image.astype(np.float32) / 255.0

    logger.info(f"Preprocessed image: raw shape={image.shape} -> model input shape={normalized.shape}")
    return normalized


def analyze_leaf_image(
    image_bytes: bytes, lang: str = "en", expected_crop: str | None = None
) -> DiseaseDetectionResult:
    """
    Full CV pipeline: preprocess -> CNN inference -> map to remedy.
    """
    if expected_crop and expected_crop not in _MODEL_CROP_PREFIXES:
        raise UnsupportedDiseaseCropError("This crop is not supported by the disease model yet.")

    preprocessed = preprocess_image(image_bytes)
    model = get_disease_model()
    expected_prefix = _MODEL_CROP_PREFIXES.get(expected_crop or "")
    if expected_prefix and hasattr(model, "predict_for_crop"):
        label, confidence, crop_probability = model.predict_for_crop(preprocessed, expected_prefix)
        if crop_probability < MIN_SELECTED_CROP_PROBABILITY:
            logger.info(
                "Rejected crop mismatch: requested=%s probability=%.3f threshold=%.2f",
                expected_crop, crop_probability, MIN_SELECTED_CROP_PROBABILITY,
            )
            raise CropMismatchPhotoError("The image does not match the stated crop.")
        logger.info(
            "Crop-conditioned prediction: crop=%s label=%s conditional_confidence=%.3f crop_probability=%.3f",
            expected_crop, label, confidence, crop_probability,
        )
        required_confidence = 0.80
    else:
        label, confidence = model.predict(preprocessed)
        if expected_prefix and not label.startswith(expected_prefix):
            logger.info("Rejected crop mismatch: requested=%s predicted=%s", expected_crop, label)
            raise CropMismatchPhotoError("The image does not match the stated crop.")
        required_confidence = MIN_DISEASE_CONFIDENCE

    if confidence < required_confidence:
        logger.info(
            "Rejected uncertain image classification: label=%s confidence=%.3f threshold=%.2f",
            label,
            confidence,
            required_confidence,
        )
        raise InvalidLeafPhotoError("Image is not confidently recognised as a supported crop leaf.")

    is_healthy = label == "Healthy" or label.lower().endswith("___healthy")
    # PlantVillage-trained labels use names such as Tomato___healthy. Healthy
    # leaves should receive the normal monitoring guidance even when the exact
    # crop-specific healthy label is not explicitly listed in REMEDIES.
    remedy_map = remedy_for_label(label) or (REMEDIES["Healthy"] if is_healthy else None)
    if remedy_map is None:
        remedy_map = {
            "hi": "इस बीमारी के लिए अभी स्वीकृत उपचार सुझाव उपलब्ध नहीं है। कृपया स्थानीय कृषि विशेषज्ञ से पुष्टि करें।",
            "en": "An approved treatment recommendation is not configured for this label. Please confirm with a local agricultural expert.",
        }
    remedy_text = (
        _PUNJABI_REMEDIES.get(label) if lang == "pa" else None
    ) or remedy_map.get(lang) or remedy_map.get("en")
    # The current classifier can identify a crop only for disease labels.  Do
    # not pretend a healthy leaf's crop is known when it has not been inferred.
    if "___" in label:
        # The trained model's class itself identifies the crop, including for
        # healthy leaves (for example: Tomato___healthy).
        crop_guess = label.split("___", 1)[0].replace("_", " ")
    elif is_healthy:
        crop_guess = "फसल की पहचान नहीं हुई" if lang == "hi" else "Crop not identified"
    else:
        crop_guess = CROP_FROM_LABEL.get(label, "Crop not identified")

    result = DiseaseDetectionResult(
        disease_name=label.replace("___", " - ").replace("_", " "),
        confidence=round(confidence, 3),
        is_healthy=is_healthy,
        remedy=remedy_text,
        crop_guess=crop_guess,
    )
    logger.info(f"Disease analysis result: {result}")
    return result
