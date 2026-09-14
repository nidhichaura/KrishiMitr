"""Generate public audio replies for WhatsApp voice-note users."""
import base64
import time
from pathlib import Path
from uuid import uuid4

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
VOICE_REPLY_DIR = Path(__file__).resolve().parent.parent / "generated_audio"
VOICE_REPLY_DIR.mkdir(exist_ok=True)
MAX_AUDIO_FILES = 100
MAX_AUDIO_AGE_SECONDS = 24 * 60 * 60

_LANGUAGE_CODES = {
    "hi": "hi-IN", "en": "en-IN", "mr": "mr-IN", "pa": "pa-IN",
    "ta": "ta-IN", "te": "te-IN",
    "bn": "bn-IN", "or": "od-IN", "kn": "kn-IN", "ml": "ml-IN",
    "gu": "gu-IN", "as": "as-IN", "ur": "ur-IN",
}


def cleanup_old_voice_replies() -> None:
    """Bound temporary public audio storage so it cannot grow forever."""
    now = time.time()
    files = sorted(VOICE_REPLY_DIR.glob("reply_*"), key=lambda item: item.stat().st_mtime, reverse=True)
    for index, path in enumerate(files):
        if index >= MAX_AUDIO_FILES or now - path.stat().st_mtime > MAX_AUDIO_AGE_SECONDS:
            try:
                path.unlink()
            except OSError as exc:
                logger.warning("Could not remove expired audio reply %s: %s", path.name, exc)


async def create_voice_reply(text: str, lang: str) -> str | None:
    """Create an WhatsApp-compatible MP3 reply and return its public URL."""
    if not settings.SARVAM_API_KEY or not settings.PUBLIC_BASE_URL:
        logger.info("Voice reply skipped: SARVAM_API_KEY or PUBLIC_BASE_URL is missing.")
        return None
    cleanup_old_voice_replies()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                settings.SARVAM_TTS_URL,
                headers={"api-subscription-key": settings.SARVAM_API_KEY},
                json={
                    "text": text[:2400],
                    "language_code": _LANGUAGE_CODES.get(lang, "hi-IN"),
                    "model": "bulbul:v3",
                    "speaker": "shubh",
                    # WhatsApp reliably accepts audio/mpeg; WAV can be fetched
                    # by Twilio but rejected by WhatsApp at delivery time.
                    "output_audio_codec": "mp3",
                },
            )
            response.raise_for_status()
            audio_base64 = response.json()["audios"][0]
        filename = f"reply_{uuid4().hex}.mp3"
        (VOICE_REPLY_DIR / filename).write_bytes(base64.b64decode(audio_base64))
        return f"{settings.PUBLIC_BASE_URL.rstrip('/')}/audio-replies/{filename}"
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        logger.warning("Sarvam voice reply failed: %s", exc)
        return None
