"""Explainable contextual crop-and-soil advisory, ready for a validated ML model."""
from __future__ import annotations
from datetime import date
import httpx

_TARGETS = {
    "wheat": (120, 25, 20, {10, 11, 12}), "rice": (100, 25, 20, {6, 7}),
    "maize": (120, 25, 20, {6, 7, 10}), "soybean": (20, 30, 20, {6, 7}),
    "tomato": (100, 40, 40, {8, 9, 10, 11}),
}

async def fetch_weather(latitude: float | None, longitude: float | None) -> dict:
    if latitude is None or longitude is None:
        return {"temperature_c": None, "rain_next_7_days_mm": None, "source": "Location not provided"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": latitude, "longitude": longitude, "current": "temperature_2m", "daily": "precipitation_sum", "forecast_days": 7, "timezone": "auto"})
            r.raise_for_status(); data = r.json()
        return {"temperature_c": float(data["current"]["temperature_2m"]), "rain_next_7_days_mm": round(sum(data["daily"]["precipitation_sum"]), 1), "source": "Open-Meteo forecast"}
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return {"temperature_c": None, "rain_next_7_days_mm": None, "source": "Forecast unavailable"}

def build_advisory(crop: str, nitrogen: float, phosphorus: float, potassium: float, ph: float, weather: dict) -> dict:
    crop = crop.lower().strip()
    if crop not in _TARGETS: raise ValueError("Choose wheat, rice, maize, soybean, or tomato.")
    if not 0 <= ph <= 14: raise ValueError("Soil pH must be between 0 and 14.")
    if min(nitrogen, phosphorus, potassium) < 0: raise ValueError("N, P and K values cannot be negative.")
    target_n, target_p, target_k, months = _TARGETS[crop]
    gaps = {"N": max(0, target_n-nitrogen), "P": max(0, target_p-phosphorus), "K": max(0, target_k-potassium)}
    score = max(0, round(100 - min(35, sum(gaps.values())/6) - (12 if ph < 6 or ph > 7.8 else 0) - (10 if (weather["rain_next_7_days_mm"] or 0) > 80 else 0)))
    notes = []
    if ph < 6: notes.append("Acidic soil: confirm liming need with the local soil-testing lab before nutrient application.")
    if ph > 7.8: notes.append("Alkaline soil: ask the local extension officer about micronutrient availability.")
    if weather["rain_next_7_days_mm"] and weather["rain_next_7_days_mm"] > 80: notes.append("Heavy rain is forecast: avoid applying fertiliser immediately before rain.")
    elif weather["rain_next_7_days_mm"] is not None and weather["rain_next_7_days_mm"] < 10: notes.append("Low rainfall is forecast: plan irrigation before applying fertiliser where possible.")
    if not notes: notes.append("Conditions look broadly suitable. Check field moisture and the local crop calendar before sowing.")
    return {"crop": crop.title(), "readiness_score": score, "sowing_status": "Suitable sowing period" if date.today().month in months else "Outside the usual sowing period", "weather": weather, "nutrient_gap_kg_per_ha": gaps, "notes": notes, "disclaimer": "Decision support only. These are demo benchmarks, not a fertiliser prescription. Confirm crop stage, soil-test method and final dose with your Krishi Vigyan Kendra or agriculture officer."}
