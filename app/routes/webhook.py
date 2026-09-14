"""
Twilio WhatsApp Webhook.

Twilio POSTs inbound WhatsApp messages here as
`application/x-www-form-urlencoded` data with fields such as:

    From, To, Body, ProfileName, NumMedia, MediaUrl0, MediaContentType0, ...

This route:
  1. Parses the inbound payload.
  2. Routes based on media type: audio -> speech pipeline, image -> vision
     pipeline, none -> direct text pipeline.
  3. Runs intent detection / disease classification / market lookup as needed.
  4. Formulates a localized response and returns it as TwiML so Twilio
     relays it straight back to the farmer on WhatsApp.
"""
from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings
from app.core.constants import Intent, MediaCategory
from app.models.schemas import DiseaseDetectionResult
from app.services import speech_service, vision_service, market_service, response_service, voice_reply_service
from app.utils.language_utils import detect_user_language, normalize_language, translate
from app.utils.media_utils import (
    download_twilio_media,
    classify_media,
    save_temp_file,
    cleanup_temp_file,
    suffix_for_content_type,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def verify_twilio_request(request: Request) -> None:
    """Reject forged webhook calls before processing farmer data or media."""
    if not settings.VERIFY_TWILIO_SIGNATURES:
        logger.warning("Twilio signature verification is disabled; use only for local testing.")
        return
    signature = request.headers.get("X-Twilio-Signature", "")
    # A proxy can make request.url internal. PUBLIC_BASE_URL preserves the
    # exact public URL that was configured in the Twilio Console.
    base_url = settings.PUBLIC_BASE_URL.rstrip("/") if settings.PUBLIC_BASE_URL else str(request.base_url).rstrip("/")
    url = f"{base_url}{request.url.path}"
    form = await request.form()
    params = {key: value for key, value in form.multi_items()}
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    if not signature or not validator.validate(url, params, signature):
        logger.warning("Rejected webhook with an invalid Twilio signature.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature.")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(""),
    ProfileName: str = Form(default=None),
    NumMedia: str = Form(default="0"),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None),
):
    """
    Primary entry point for all inbound WhatsApp traffic (text / voice / image).
    Always returns HTTP 200 with a TwiML <Response> so Twilio doesn't retry.
    """
    await verify_twilio_request(request)
    logger.info(
        f"Inbound WhatsApp message from={From} profile={ProfileName} "
        f"num_media={NumMedia} content_type={MediaContentType0} body='{Body[:50]}'"
    )

    twiml = MessagingResponse()

    try:
        num_media = int(NumMedia) if NumMedia and NumMedia.isdigit() else 0
        response_text, response_lang = await route_incoming_message_with_language(
            body=Body,
            num_media=num_media,
            media_url=MediaUrl0,
            media_content_type=MediaContentType0,
        )
    except Exception:
        logger.exception(f"Unhandled error while processing message from {From}")
        fallback_lang = detect_user_language(Body) if Body else "hi"
        response_text = translate("processing_error", fallback_lang)
        response_lang = fallback_lang

    message = twiml.message(response_text)
    # Send the written response plus a spoken version for every WhatsApp
    # interaction. This makes photo and text responses usable for farmers who
    # cannot comfortably read. TTS safely degrades to text only when Sarvam
    # credentials/public URL have not been configured.
    audio_url = await voice_reply_service.create_voice_reply(response_text, response_lang)
    if audio_url:
        message.media(audio_url)
    # Twilio's webhook reply is XML.  Send explicit UTF-8 bytes and charset so
    # Odia and every other native Indic script reaches WhatsApp unchanged.
    return Response(
        content=str(twiml).encode("utf-8"),
        headers={"Content-Type": "application/xml; charset=utf-8"},
    )


async def route_incoming_message(
    body: str,
    num_media: int,
    media_url: str | None,
    media_content_type: str | None,
) -> str:
    response_text, _ = await route_incoming_message_with_language(body, num_media, media_url, media_content_type)
    return response_text


async def route_incoming_message_with_language(
    body: str, num_media: int, media_url: str | None, media_content_type: str | None,
) -> tuple[str, str]:
    """
    Core routing logic shared by the webhook handler. Kept separate from the
    FastAPI route function so it's directly unit-testable without an HTTP layer.
    """
    # --- Case 1: No media -> plain text message ---
    if num_media <= 0 or not media_url:
        text, intent_result, lang = speech_service.process_text_input(body)
        return await handle_text_intent(text, intent_result.intent, lang, intent_result.entities), lang

    media_category = classify_media(media_content_type)

    # --- Case 2: Voice note -> Bhashini/Sarvam ASR + intent detection ---
    if media_category == MediaCategory.AUDIO:
        audio_bytes = await download_twilio_media(media_url)
        try:
            transcription = await speech_service.transcribe_audio(
                audio_bytes,
                language_hint="hi",
                filename=f"voice{suffix_for_content_type(media_content_type) or '.ogg'}",
                content_type=media_content_type or "audio/ogg",
            )
        except speech_service.SpeechRecognitionUnavailable as exc:
            lang = normalize_language(exc.language, default="hi")
            return translate("voice_service_unavailable", lang), lang
        intent_result = speech_service.detect_intent(transcription.transcript)
        lang = normalize_language(transcription.detected_language, default=detect_user_language(transcription.transcript))
        return await handle_text_intent(
            transcription.transcript,
            intent_result.intent,
            lang,
            intent_result.entities,
        ), lang

    # --- Case 3: Leaf image -> OpenCV preprocessing + EfficientNet CNN ---
    if media_category == MediaCategory.IMAGE:
        lang = detect_user_language(body) if body else "hi"
        # A crop name is optional: farmers can send only a photo. When it is
        # supplied, it becomes an extra crop-match guard against mislabeling.
        expected_crop = speech_service.extract_commodity(body) if body else None
        if not expected_crop:
            return translate("ask_photo_with_crop", lang), lang
        image_bytes = await download_twilio_media(media_url)

        temp_path = save_temp_file(image_bytes, suffix=suffix_for_content_type(media_content_type) or ".jpg")
        try:
            disease_result: DiseaseDetectionResult = vision_service.analyze_leaf_image(
                image_bytes, lang=lang, expected_crop=expected_crop
            )
        except vision_service.CropMismatchPhotoError:
            logger.info("Rejected image because it does not match the named crop")
            return translate("crop_photo_mismatch", lang, crop=expected_crop), lang
        except vision_service.UnsupportedDiseaseCropError:
            return translate("disease_crop_unsupported", lang, crop=expected_crop), lang
        except vision_service.MissingDiseaseCropError:
            return translate("ask_photo_with_crop", lang), lang
        except vision_service.InvalidLeafPhotoError:
            logger.info("Rejected unusable/non-leaf image from WhatsApp user")
            return translate("invalid_leaf_photo", lang), lang
        finally:
            cleanup_temp_file(temp_path)

        return response_service.build_response(Intent.DISEASE_CHECK.value, lang, disease_result=disease_result), lang

    # --- Case 4: Unsupported media type (e.g. video, document, location pin) ---
    lang = detect_user_language(body) if body else "hi"
    return response_service.build_response(Intent.UNSUPPORTED_MEDIA.value, lang), lang


async def handle_text_intent(text: str, intent: str, lang: str, entities: dict) -> str:
    """
    Given a resolved transcript/text + classified intent, run the appropriate
    downstream pipeline (market lookup, disease-check prompt, greeting, etc.)
    and build the final localized message.
    """
    normalized_text = text.casefold()
    state_for_list = speech_service.extract_state(text)
    # Keep this separate from price-intent detection: asking "which crops are
    # available" has no commodity, so it would otherwise fall through to the
    # generic unknown reply.  Include native-script phrases used by farmers.
    list_markers = (
        "available crop", "available crops", "which crop", "which crops",
        "crop list", "crops in",
        # Hindi / Marathi / Punjabi
        "kaun si fasal", "कौन सी फसल", "फसल सूची", "कोणती पिके", "कोणते पीक",
        "ਕਿਹੜੀਆਂ ਫਸਲਾਂ", "ਕਿਹੜੀ ਫਸਲ",
        # Bengali / Assamese / Odia
        "কোন ফসল", "ফসল তালিকা", "কি শস্য", "শস্য তালিকা",
        "କେଉଁ ଫସଲ", "ଫସଲ ତାଲିକା", "କେଉଁ ଚାଷ",
        # Tamil / Telugu / Kannada / Malayalam / Gujarati / Urdu
        "எந்த பயிர்கள்", "பயிர் பட்டியல்", "ఏ పంటలు", "పంటల జాబితా",
        "ಯಾವ ಬೆಳೆ", "ಬೆಳೆಗಳ ಪಟ್ಟಿ", "ഏത് വിളകൾ", "വിളകളുടെ പട്ടിക",
        "કયા પાક", "પાકની યાદી", "کون سی فصل", "فصلوں کی فہرست",
    )
    if state_for_list and any(marker in normalized_text for marker in list_markers):
        crops = market_service.list_available_commodities(state_for_list)
        if not crops:
            return translate("available_crops_unavailable", lang, state=state_for_list)
        displayed_crops = crops[:25]
        crop_text = ", ".join(displayed_crops)
        if len(crops) > len(displayed_crops):
            crop_text += f" … (+{len(crops) - len(displayed_crops)} more)"
        return translate(
            "available_crops", lang, state=state_for_list,
            crops=crop_text, example=displayed_crops[0],
        )

    if intent == Intent.MARKET_PRICE.value:
        commodity = entities.get("commodity")
        if not commodity:
            return response_service.build_response(Intent.MARKET_PRICE.value, lang, market_result=None)
        # Never silently substitute Punjab/any other state when the farmer did
        # not say where they want to sell.
        state = entities.get("state")
        if not state:
            return response_service.build_response(Intent.MARKET_PRICE.value, lang, market_result=None)
        market_result = market_service.fetch_market_price(commodity, state=state)
        if market_result is None:
            # Crop and state were already supplied. Do not ask the farmer to
            # repeat them when the official source is simply unavailable.
            return translate(
                "market_price_source_unavailable", lang,
                commodity=commodity.title(), state=state,
            )
        return response_service.build_response(Intent.MARKET_PRICE.value, lang, market_result=market_result)

    if intent == Intent.DISEASE_CHECK.value:
        # Farmer described a symptom in text/voice but hasn't sent a photo yet.
        return response_service.build_response(Intent.DISEASE_CHECK.value, lang, disease_result=None)

    # Greeting / weather / unknown all fall through to the generic templated response.
    return response_service.build_response(intent, lang)
