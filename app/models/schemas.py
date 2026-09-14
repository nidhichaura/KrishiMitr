"""
Pydantic data models used internally between services/routes.
Note: The raw inbound Twilio webhook is application/x-www-form-urlencoded,
so it's parsed via FastAPI `Form(...)` params directly in the route
(see app/routes/webhook.py) rather than as a JSON request body model.
These schemas represent the *normalized* internal representation.
"""
from typing import Optional
from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    """Normalized representation of an inbound WhatsApp message."""
    from_number: str
    to_number: str
    profile_name: Optional[str] = None
    raw_body: str = ""
    num_media: int = 0
    media_url: Optional[str] = None
    media_content_type: Optional[str] = None


class TranscriptionResult(BaseModel):
    transcript: str
    detected_language: str
    confidence: float = Field(ge=0.0, le=1.0)


class IntentResult(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: dict = Field(default_factory=dict)


class DiseaseDetectionResult(BaseModel):
    disease_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_healthy: bool
    remedy: str
    crop_guess: Optional[str] = None


class MarketPriceResult(BaseModel):
    commodity: str
    state: str
    mandi: str
    min_price_per_quintal: float
    max_price_per_quintal: float
    modal_price_per_quintal: float
    price_date: str
    variety: Optional[str] = None
    source: str = "AGMARKNET via data.gov.in"


class OutboundResponse(BaseModel):
    to_number: str
    body: str
    language: str
