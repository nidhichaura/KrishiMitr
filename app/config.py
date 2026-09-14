"""
Centralized configuration for KrishiMitr backend.
Reads from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Twilio
    TWILIO_ACCOUNT_SID: str = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    TWILIO_AUTH_TOKEN: str = "mock_auth_token"
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"

    # Exotel programmable voice / IVR. Set these only in .env (never commit
    # account credentials). EXOTEL_PUBLIC_BASE_URL must be public HTTPS.
    EXOTEL_ACCOUNT_SID: str | None = None
    EXOTEL_API_KEY: str | None = None
    EXOTEL_API_TOKEN: str | None = None
    EXOTEL_EXOPHONE: str | None = None
    EXOTEL_PUBLIC_BASE_URL: str | None = None

    # App
    APP_ENV: str = "development"
    DEFAULT_LANGUAGE: str = "hi"
    LOG_LEVEL: str = "INFO"
    # Comma-separated browser origins. Keep this restrictive in production.
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    # Set this to false only for local webhook testing without Twilio.
    VERIFY_TWILIO_SIGNATURES: bool = True
    MAX_IMAGE_UPLOAD_BYTES: int = 8 * 1024 * 1024
    API_RATE_LIMIT_PER_MINUTE: int = 20
    # Digits only, e.g. 919876543210. Shown as the website's WhatsApp CTA.
    PUBLIC_WHATSAPP_NUMBER: str | None = None

    # Consent-first business features. SQLite is adequate for a pilot; use a
    # managed database and a secret manager before production rollout.
    BUSINESS_DB_PATH: str = "data/krishimitr_business.db"
    PARTNER_API_TOKEN: str | None = None
    INSIGHTS_MINIMUM_COHORT: int = 20

    # External AI service base URLs (for future real integration)
    BHASHINI_API_URL: str = "https://mock-bhashini.local/api/v1"
    SARVAM_API_URL: str = "https://mock-sarvam.local/api/v1"
    # Sarvam AI: real Indian-language ASR and TTS for WhatsApp voice notes.
    # Keep this secret in .env only. When unset, the app never guesses a transcript.
    SARVAM_API_KEY: str | None = None
    SARVAM_ASR_URL: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"
    # Public HTTPS base URL (for example your ngrok URL). Twilio uses this to
    # download the generated voice reply.
    PUBLIC_BASE_URL: str | None = None
    # Government of India OGD / AGMARKNET daily mandi-price dataset.
    # Create an API key at data.gov.in and keep it only in .env, never in git.
    DATA_GOV_API_KEY: str | None = None
    DATA_GOV_RESOURCE_ID: str = "9ef84268-d588-465a-a308-a864a43d0070"
    DATA_GOV_API_URL: str = "https://api.data.gov.in/resource"
    # Agmarknet 2.0 is the current public market-data platform operated by
    # the Ministry of Agriculture. Its public daily-report endpoint does not
    # require an API key and is used as the primary mandi-price source.
    AGMARKNET_API_URL: str = "https://api.agmarknet.gov.in/v1"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't re-parse env on every import."""
    return Settings()


settings = get_settings()
