"""Location-based weather lookup used to pre-fill field advisory inputs."""
import httpx


_PLACE_TRANSLATIONS = {
    "Ludhiana - Chandigarh Highway": ("लुधियाना - चंडीगढ़ राजमार्ग", "Ludhiana - Chandigarh Highway"),
    "Ludhiana-Chandigarh Highway": ("लुधियाना-चंडीगढ़ राजमार्ग", "Ludhiana-Chandigarh Highway"),
    "Gharuan": ("घरुआं", "Gharuan"), "Chandigarh": ("चंडीगढ़", "Chandigarh"),
    "Punjab": ("पंजाब", "Punjab"), "ਪੰਜਾਬ": ("पंजाब", "Punjab"),
    "Haryana": ("हरियाणा", "Haryana"), "हरियाणा": ("हरियाणा", "Haryana"),
    "Madhya Pradesh": ("मध्य प्रदेश", "Madhya Pradesh"), "मध्य प्रदेश": ("मध्य प्रदेश", "Madhya Pradesh"),
    "Panipat": ("पानीपत", "Panipat"), "Dewas": ("देवास", "Dewas"),
}


def _regional_soil_baseline(latitude: float, longitude: float) -> dict:
    """Return a conservative regional baseline, never a substitute for a soil test.

    Weather can be measured at a coordinate. Soil NPK and pH cannot: they vary
    within a field. These values only prevent the form from using unrelated
    defaults after a farmer has shared their location.
    """
    if latitude >= 27 and 68 <= longitude <= 80:  # Indo-Gangetic plains
        return {"nitrogen": 75, "phosphorus": 45, "potassium": 35, "ph": 7.0}
    if latitude < 19:  # southern peninsular belt
        return {"nitrogen": 70, "phosphorus": 40, "potassium": 45, "ph": 6.5}
    if longitude >= 78:  # central/eastern belt
        return {"nitrogen": 65, "phosphorus": 40, "potassium": 40, "ph": 6.4}
    return {"nitrogen": 60, "phosphorus": 40, "potassium": 35, "ph": 6.5}


def _localize_place(label: str, language: str) -> str:
    """Normalise common Indian locality labels so one UI never mixes scripts."""
    target = 0 if language == "hi" else 1
    for source, pair in _PLACE_TRANSLATIONS.items():
        label = label.replace(source, pair[target])
    return label


def fetch_location_weather(latitude: float, longitude: float) -> dict | None:
    try:
        response = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": latitude, "longitude": longitude, "current": "temperature_2m",
                    "daily": "precipitation_sum", "forecast_days": 1, "timezone": "auto"},
            timeout=httpx.Timeout(8.0, connect=3.0),
        )
        response.raise_for_status()
        data = response.json()
        return {
            "temperature": data["current"]["temperature_2m"],
            "rainfall": data["daily"]["precipitation_sum"][0],
            **_regional_soil_baseline(latitude, longitude),
            "source": "Open-Meteo weather forecast",
            "soil_source": "Regional soil baseline estimate; confirm with a soil test",
        }
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None


def reverse_geocode(latitude: float, longitude: float, language: str = "en") -> str | None:
    """Turn consented coordinates into a short, farmer-readable place label."""
    try:
        response = httpx.get("https://nominatim.openstreetmap.org/reverse", params={
            "lat": latitude, "lon": longitude, "format": "jsonv2", "zoom": 18,
        }, headers={"User-Agent": "KrishiMitr farmer-advisory/1.0", "Accept-Language": "hi,en" if language == "hi" else "en"}, timeout=httpx.Timeout(8.0, connect=3.0))
        response.raise_for_status()
        address = response.json().get("address", {})
        parts = [address.get(key) for key in ("house_number", "road", "neighbourhood", "suburb", "city", "town", "village", "state")]
        label = ", ".join(dict.fromkeys(str(part).strip() for part in parts if part))
        raw = label or response.json().get("display_name", "").split(",", 3)[0]
        return _localize_place(raw, language) if raw else None
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        return None
