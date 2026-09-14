"""Speech recognition and multilingual intent detection."""
import unicodedata
import json
import re
from typing import Tuple

import httpx

from app.config import settings
from app.core.constants import Intent, COMMODITY_KEYWORDS
from app.models.schemas import TranscriptionResult, IntentResult
from app.utils.language_utils import detect_response_language
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SpeechRecognitionUnavailable(RuntimeError):
    """Raised when real voice recognition is not configured or fails."""

    def __init__(self, message: str, language: str = "hi"):
        super().__init__(message)
        self.language = language


async def transcribe_audio(
    audio_bytes: bytes,
    language_hint: str = "hi",
    filename: str = "voice.ogg",
    content_type: str = "audio/ogg",
) -> TranscriptionResult:
    """Transcribe a WhatsApp voice note with Sarvam Saaras.

    Crop and mandi names are sent as key terms, which materially improves
    recognition of words such as sugarcane, soybean, and local crop names.
    No random/mock transcript is ever returned.
    """
    if not audio_bytes:
        raise ValueError("Empty audio payload received for transcription.")
    if not settings.SARVAM_API_KEY:
        raise SpeechRecognitionUnavailable("SARVAM_API_KEY is not configured.")

    # Voice-note users may speak any regional language.  Let Saaras identify
    # the spoken language instead of forcing every recording through Hindi.
    language_code = "unknown"
    keyterms = [
        "sugarcane", "ganna", "गन्ना", "soybean", "soyabean", "सोयाबीन",
        "cotton", "kapas", "कपास", "paddy", "rice", "धान", "चावल",
        "mandi", "मंडी", "quintal", "क्विंटल",
    ]
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                settings.SARVAM_ASR_URL,
                headers={"api-subscription-key": settings.SARVAM_API_KEY},
                files={"file": (filename, audio_bytes, content_type)},
                data={
                    # Keyterm prompting is supported by Saaras v4. It helps
                    # avoid crop-name substitutions such as sugarcane/cotton.
                    "model": "saaras:v4",
                    "mode": "transcribe",
                    "language_code": language_code,
                    "keyterms": json.dumps(keyterms, ensure_ascii=False),
                },
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Sarvam speech recognition failed (%s): %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        raise SpeechRecognitionUnavailable("Speech recognition service is unavailable.") from exc
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("Sarvam speech recognition failed: %s", exc)
        raise SpeechRecognitionUnavailable("Speech recognition service is unavailable.") from exc

    detected_language = str(payload.get("language_code", language_code)).split("-")[0]
    transcript = str(payload.get("transcript", "")).strip()
    if not transcript:
        raise SpeechRecognitionUnavailable("No speech was recognised in the voice note.", detected_language)
    # Saaras may provide a confidence field. When it explicitly says that the
    # audio is unclear, asking the farmer to repeat is safer than acting on a
    # misheard crop, state, or price request. Older API payloads without this
    # field remain supported.
    raw_confidence = payload.get("confidence", payload.get("confidence_score", 0.95))
    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError):
        confidence = 0.95
    if confidence < 0.55:
        raise SpeechRecognitionUnavailable("Voice note is too noisy or unclear.", detected_language)
    result = TranscriptionResult(transcript=transcript, detected_language=detected_language, confidence=confidence)
    logger.info("Sarvam transcribed voice note (%s): %s", detected_language, transcript[:100])
    return result


# Keyword sets for rule-based multilingual intent detection.
_INTENT_KEYWORDS = {
    Intent.MARKET_PRICE: [
        "price", "rate", "भाव", "रेट", "दाम", "kimat", "keemat", "kitna", "market",
        "mandi", "मंडी", "ਮੰਡੀ", "ਬਾਜ਼ਾਰ", "sell", "bech", "bhav", "daam", "dara",
        "vilai", "dhara", "bele", "vila", "bhau", "dam", "dor", "rate",
        "দাম", "দর", "বাজার", "ମୂଲ୍ୟ", "ଦର", "ମଣ୍ଡି", "ಬೆಲೆ", "ಮಂಡಿ",
        "വില", "മണ്ടി", "ભાવ", "બજાર", "ਕੀਮਤ", "ਭਾਅ", "ਦਰ",
        "விலை", "ధర", "ಬೆಲೆ", "വില", "ભાવ", "দাম", "দৰ", "قیمت", "دام",
    ],
    Intent.DISEASE_CHECK: [
        "disease", "बीमारी", "रोग", "pest", "कीट", "spots", "धब्बे", "yellow",
        "पीले", "sukh", "सूख", "kharab", "खराब", "leaf", "पत्ते", "पत्ता",
        "রোগ", "পোকা", "পাতা", "ରୋଗ", "ପୋକ", "ପତ୍ର", "ರೋಗ", "ಕೀಟ", "ಎಲೆ",
        "രോഗം", "കീടം", "ഇല", "રોગ", "જીવાત", "પાન",
    ],
    Intent.WEATHER: [
        "weather", "मौसम", "बारिश", "rain", "baarish", "temperature", "तापमान",
    ],
    Intent.GREETING: [
        "hi", "hello", "namaste", "नमस्ते", "namaskar", "नमस्कार", "hey",
        "নমস্কার", "নমস্তে", "ନମସ୍କାର", "ನಮಸ್ಕಾರ", "നമസ്കാരം", "નમસ્તે",
    ],
}

# A state is required before a price can be looked up.  The market returned by
# AGMARKNET is shown in the reply; a future UI/location-pin flow can add a
# precise mandi filter without changing the price service.
_STATE_ALIASES = {
    "Uttar Pradesh": ["uttar pradesh", "u.p.", "up", "उत्तर प्रदेश", "यूपी"],
    "Madhya Pradesh": ["madhya pradesh", "m.p.", "mp", "मध्य प्रदेश", "एमपी"],
    "Punjab": ["punjab", "पंजाब", "ਪੰਜਾਬ"],
    "Maharashtra": ["maharashtra", "महाराष्ट्र", "মহারাষ্ট্র"],
    "Gujarat": ["gujarat", "गुजरात", "ગુજરાત"],
    "Rajasthan": ["rajasthan", "राजस्थान"],
    "Bihar": ["bihar", "बिहार"],
    "Karnataka": ["karnataka", "कर्नाटक", "ಕರ್ನಾಟಕ"],
    "Andhra Pradesh": ["andhra pradesh", "a.p.", "andhra", "आंध्र प्रदेश", "ఆంధ్ర ప్రదేశ్"],
    "Arunachal Pradesh": ["arunachal pradesh", "arunachal", "अरुणाचल प्रदेश"],
    "Assam": ["assam", "অসম", "আসাম"],
    "Chhattisgarh": ["chhattisgarh", "chattisgarh", "छत्तीसगढ़", "ছত্তীসগঢ়"],
    "Goa": ["goa", "गोवा", "গোয়া", "ଗୋଆ", "ಗೋವಾ"],
    "Haryana": ["haryana", "हरियाणा", "হরিয়ানা"],
    "Himachal Pradesh": ["himachal pradesh", "himachal", "हिमाचल प्रदेश"],
    "Jharkhand": ["jharkhand", "झारखंड", "ঝাড়খণ্ড"],
    "Kerala": ["kerala", "केरल", "കേരളം"],
    "Manipur": ["manipur", "मणिपुर", "মণিপুর"],
    "Meghalaya": ["meghalaya", "मेघालय", "মেঘালয়"],
    "Mizoram": ["mizoram", "मिजोरम", "মিজোরাম"],
    "Nagaland": ["nagaland", "नागालैंड", "নাগাল্যান্ড"],
    "Odisha": [
        "odisha", "orissa", "ओडिशा", "ଓଡ଼ିଶା", "ওড়িশা", "ওডিশা",
        "ਓਡੀਸ਼ਾ", "ஒடிசா", "ఒడిశా", "ಒಡಿಶಾ", "ഒഡീഷ", "ઓડિશા", "اوڈیشہ",
    ],
    "Sikkim": ["sikkim", "सिक्किम", "সিকিম"],
    "Tamil Nadu": ["tamil nadu", "tamilnadu", "तमिलनाडु", "தமிழ்நாடு"],
    "Telangana": ["telangana", "तेलंगाना", "తెలంగాణ"],
    "Tripura": ["tripura", "त्रिपुरा", "ত্রিপুরা"],
    "Uttarakhand": ["uttarakhand", "उत्तराखंड", "উত্তরাখণ্ড"],
    "West Bengal": ["west bengal", "bengal", "পশ্চিমবঙ্গ", "পশ্চিম বাংলা", "পশ্চিমবঙ্গ"],
    "Delhi": ["delhi", "new delhi", "दिल्ली", "দিল্লি"],
    "Jammu and Kashmir": ["jammu and kashmir", "jammu", "kashmir", "जम्मू और कश्मीर"],
    "Ladakh": ["ladakh", "लद्दाख"],
    "Puducherry": ["puducherry", "pondicherry", "पुडुचेरी", "புதுச்சேரி"],
    "Chandigarh": ["chandigarh", "चंडीगढ़", "চণ্ডীগড়"],
    "Dadra and Nagar Haveli and Daman and Diu": ["dadra and nagar haveli", "daman and diu", "दादरा और नगर हवेली", "दमन और दीव"],
    "Lakshadweep": ["lakshadweep", "लक्षद्वीप", "ലക്ഷദ്വീപ്"],
    "Andaman and Nicobar Islands": ["andaman", "nicobar", "अंडमान", "নিকোবর"],
}


def detect_intent(text: str) -> IntentResult:
    """
    Rule-based, multilingual keyword-matching intent classifier.

    A production system would swap this for a fine-tuned IndicBERT / mBERT
    classifier served behind Bhashini or a custom NLU endpoint — the return
    contract (IntentResult) is designed to stay stable across that swap.
    """
    if not text or not text.strip():
        return IntentResult(intent=Intent.UNKNOWN.value, confidence=0.0, entities={})

    normalized = unicodedata.normalize("NFC", text.lower().strip())

    scores = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw.lower() in normalized)
        if matches:
            scores[intent] = matches

    if not scores:
        return IntentResult(intent=Intent.UNKNOWN.value, confidence=0.3, entities={})

    best_intent = max(scores, key=scores.get)
    total_matches = sum(scores.values())
    confidence = min(0.95, 0.5 + (scores[best_intent] / max(total_matches, 1)) * 0.45)

    entities = {}
    if best_intent == Intent.MARKET_PRICE:
        commodity = extract_commodity(normalized)
        if commodity:
            entities["commodity"] = commodity
        state = extract_state(normalized)
        if state:
            entities["state"] = state

    result = IntentResult(intent=best_intent.value, confidence=round(confidence, 3), entities=entities)
    logger.info(f"Detected intent: {result.intent} (confidence={result.confidence}, entities={result.entities})")
    return result


def extract_commodity(text: str) -> str | None:
    """Find a known commodity name/alias inside free text (any supported language)."""
    normalized = unicodedata.normalize("NFC", text.lower())
    for canonical_name, aliases in COMMODITY_KEYWORDS.items():
        for alias in aliases:
            # Word boundaries prevent e.g. the commodity "rice" from
            # matching the word "price". Native-script aliases do not need
            # this guard because they cannot occur inside English words.
            if (alias.isascii() and re.search(r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)", normalized)) or (not alias.isascii() and alias.lower() in normalized):
                return canonical_name
    return None


def extract_state(text: str) -> str | None:
    """Find a supported state mention without assuming a default state."""
    normalized = unicodedata.normalize("NFC", text.lower())
    for canonical_name, aliases in _STATE_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return canonical_name
    return None


def process_text_input(text: str) -> Tuple[str, IntentResult, str]:
    """
    Convenience wrapper for plain text (non-audio) messages:
    detect language + detect intent in one call.
    Returns: (original_text, intent_result, detected_language)
    """
    lang = detect_response_language(text)
    intent_result = detect_intent(text)
    return text, intent_result, lang
