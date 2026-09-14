"""
Response Delivery Layer (formulation half).

Takes the structured result of whichever pipeline ran (market price / disease
detection / greeting / fallback) and formats it into a single localized
WhatsApp message string, ready to be sent by twilio_service.
"""
from typing import Optional

from app.core.constants import Intent
from app.models.schemas import MarketPriceResult, DiseaseDetectionResult
from app.utils.language_utils import translate
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_market_price_response(result: Optional[MarketPriceResult], lang: str) -> str:
    if result is None:
        return translate("market_price_unavailable", lang)
    return translate(
        "market_price_result",
        lang,
        commodity=result.commodity,
        mandi=result.mandi,
        state=result.state,
        min_price=result.min_price_per_quintal,
        max_price=result.max_price_per_quintal,
        modal_price=result.modal_price_per_quintal,
        date=result.price_date,
        variety=result.variety or "Not specified",
        source=result.source,
    )


def build_disease_response(result: DiseaseDetectionResult, lang: str) -> str:
    return translate(
        "disease_result",
        lang,
        crop=result.crop_guess,
        disease=result.disease_name,
        confidence=round(result.confidence * 100, 1),
        remedy=result.remedy,
    )


def build_response(intent: str, lang: str, *, market_result: Optional[MarketPriceResult] = None,
                    disease_result: Optional[DiseaseDetectionResult] = None) -> str:
    """
    Central dispatcher: given the classified intent and any pipeline output,
    produce the final localized text to send back to the farmer.
    """
    if intent == Intent.GREETING.value:
        message = translate("greeting", lang)

    elif intent == Intent.MARKET_PRICE.value:
        message = build_market_price_response(market_result, lang)

    elif intent == Intent.DISEASE_CHECK.value:
        if disease_result is not None:
            message = build_disease_response(disease_result, lang)
        else:
            message = translate("ask_for_image", lang)

    elif intent == Intent.UNSUPPORTED_MEDIA.value:
        message = translate("unsupported_media", lang)

    else:
        message = translate("unknown_intent", lang)

    logger.info(f"Built response for intent='{intent}' lang='{lang}': {message[:80]}...")
    return message
