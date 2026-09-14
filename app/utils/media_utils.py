"""
Helpers for downloading inbound WhatsApp media from Twilio's media URLs
and managing temporary files on disk.
"""
import os
import uuid
import tempfile
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.utils.logger import get_logger
from app.core.constants import MediaCategory

logger = get_logger(__name__)


async def download_twilio_media(media_url: str) -> bytes:
    """
    Download a media file from a Twilio-hosted MediaUrl.
    Twilio media URLs require HTTP Basic Auth using the Account SID / Auth Token.
    """
    parsed = urlparse(media_url)
    allowed_hosts = {"api.twilio.com", "media.twiliocdn.com"}
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError("Media URL is not a permitted Twilio HTTPS URL.")
    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        async with client.stream("GET", media_url, auth=auth) as response:
            response.raise_for_status()
            declared_size = int(response.headers.get("content-length", "0"))
            if declared_size > settings.MAX_IMAGE_UPLOAD_BYTES:
                raise ValueError("Media file is too large.")
            chunks, total = [], 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > settings.MAX_IMAGE_UPLOAD_BYTES:
                    raise ValueError("Media file is too large.")
                chunks.append(chunk)
            content = b"".join(chunks)
        logger.info("Downloaded Twilio media (%d bytes)", len(content))
        return content


def classify_media(content_type: Optional[str]) -> MediaCategory:
    """Classify a MIME content-type string into a broad media category."""
    if not content_type:
        return MediaCategory.NONE
    content_type = content_type.lower()
    if content_type.startswith("audio/") or content_type in ("application/ogg",):
        return MediaCategory.AUDIO
    if content_type.startswith("image/"):
        return MediaCategory.IMAGE
    return MediaCategory.UNSUPPORTED


def save_temp_file(data: bytes, suffix: str = ".bin") -> str:
    """Persist bytes to a uniquely named temp file and return its path."""
    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, f"krishimitr_{uuid.uuid4().hex}{suffix}")
    with open(file_path, "wb") as f:
        f.write(data)
    return file_path


def cleanup_temp_file(file_path: str) -> None:
    """Best-effort removal of a temp file. Never raises."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError as exc:
        logger.warning(f"Failed to remove temp file {file_path}: {exc}")


def suffix_for_content_type(content_type: Optional[str]) -> str:
    """Map a MIME type to a reasonable file extension for temp storage."""
    mapping = {
        "audio/ogg": ".ogg",
        "audio/opus": ".opus",
        "audio/mpeg": ".mp3",
        "audio/mp4": ".m4a",
        "audio/amr": ".amr",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get((content_type or "").lower(), "")
