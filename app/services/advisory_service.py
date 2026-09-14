"""Explainable nearest-profile advisory baseline for field-level crop guidance.

This is deliberately a decision-support model, not a fertiliser prescription.
It compares entered NPK, pH and weather conditions with agronomy reference
profiles, then reports the closest suitable crop and the nutrient gap.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class CropProfile:
    crop: str
    n: float
    p: float
    k: float
    ph: float
    temperature: float
    rainfall: float
    sowing: str


PROFILES = (
    CropProfile("Wheat", 75, 45, 35, 7.0, 20, 55, "October to December"),
    CropProfile("Rice", 85, 45, 40, 6.2, 28, 190, "June to July"),
    CropProfile("Maize", 80, 45, 40, 6.5, 25, 90, "June to July"),
    CropProfile("Tomato", 70, 45, 55, 6.5, 24, 65, "September to November"),
    CropProfile("Soybean", 30, 40, 35, 6.5, 26, 80, "June to July"),
    CropProfile("Onion", 60, 35, 50, 6.4, 22, 45, "October to December"),
)


def _distance(profile: CropProfile, n: float, p: float, k: float, ph: float, temp: float, rain: float) -> float:
    # Scale each feature to comparable agronomic variation. Lower is a better
    # contextual match; the output is never represented as yield prediction.
    return sqrt(
        ((n - profile.n) / 35) ** 2 + ((p - profile.p) / 25) ** 2 +
        ((k - profile.k) / 30) ** 2 + ((ph - profile.ph) / 1.2) ** 2 +
        ((temp - profile.temperature) / 10) ** 2 + ((rain - profile.rainfall) / 80) ** 2
    )


def recommend(*, nitrogen: float, phosphorus: float, potassium: float, ph: float,
              temperature: float, rainfall: float, crop: str | None = None, question: str | None = None) -> dict:
    candidates = [item for item in PROFILES if item.crop.casefold() == crop.casefold()] if crop else list(PROFILES)
    candidates = candidates or list(PROFILES)
    best = min(candidates, key=lambda item: _distance(item, nitrogen, phosphorus, potassium, ph, temperature, rainfall))
    distance = _distance(best, nitrogen, phosphorus, potassium, ph, temperature, rainfall)
    nutrient_gaps = {
        "nitrogen": round(best.n - nitrogen), "phosphorus": round(best.p - phosphorus), "potassium": round(best.k - potassium),
    }
    gaps = [name for name, gap in nutrient_gaps.items() if gap > 10]
    asked = (question or "").casefold()
    answer_kind = "nutrient" if any(word in asked for word in ("fertil", "urea", "खाद", "उर्वरक")) else "sowing" if any(word in asked for word in ("sow", "plant", "बो", "बुआई")) else "general"
    return {
        "recommended_crop": best.crop,
        "sowing_window": best.sowing,
        "fit": "good" if distance < 1.6 else "check_conditions",
        "nutrient_gaps": nutrient_gaps,
        "priority": gaps[0] if gaps else "balanced",
        "answer_kind": answer_kind,
        "disclaimer": "Decision support only. Confirm fertiliser quantity with a recent soil test and local agriculture officer.",
    }
