"""Public, mobile-first web interface and its safe JSON endpoints."""
from pathlib import Path
import re

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, Response

from app.config import settings
from app.services import advisory_service, market_service, response_service, speech_service, vision_service
from app.utils.rate_limit import enforce_api_rate_limit

router = APIRouter()
_INDEX = Path(__file__).resolve().parents[1] / "static" / "index.html"
_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/", include_in_schema=False)
async def farmer_home():
    number = re.sub(r"\D", "", settings.PUBLIC_WHATSAPP_NUMBER or "")
    whatsapp_link = f"https://wa.me/{number}" if number else "#help"
    page = _INDEX.read_text(encoding="utf-8").replace("__WHATSAPP_LINK__", whatsapp_link)
    return HTMLResponse(page.replace("__WHATSAPP_READY__", "true" if number else "false"))


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Avoid a distracting 404 when a browser asks for the optional icon."""
    return Response(status_code=204)


@router.post("/api/disease/analyze")
async def analyze_disease(
    request: Request,
    image: UploadFile = File(...),
    crop: str | None = Form(default=None),
    language: str = Form(default="hi"),
):
    enforce_api_rate_limit(request)
    if image.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Upload a JPG, PNG, or WEBP leaf photo.")
    image_bytes = await image.read(settings.MAX_IMAGE_UPLOAD_BYTES + 1)
    if not image_bytes or len(image_bytes) > settings.MAX_IMAGE_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 8 MB or smaller.")
    try:
        normalized_crop = speech_service.extract_commodity(crop) if crop else None
        result = await run_in_threadpool(vision_service.analyze_leaf_image, image_bytes, language, normalized_crop)
    except vision_service.MissingDiseaseCropError:
        raise HTTPException(status_code=422, detail="Select the crop before checking a leaf photo.")
    except vision_service.UnsupportedDiseaseCropError:
        raise HTTPException(status_code=422, detail="Disease screening for this crop is not available yet.")
    except (vision_service.InvalidLeafPhotoError, vision_service.CropMismatchPhotoError):
        raise HTTPException(status_code=422, detail="Please upload one clear, close, well-lit photo of a leaf.")
    return {
        "result": result.model_dump(),
        "message": response_service.build_disease_response(result, language),
        "disclaimer": "This is an initial photo screening. Confirm treatment and dosage with a local agricultural expert.",
    }


@router.get("/api/market/price")
async def market_price(request: Request, commodity: str, state: str, mandi: str | None = None):
    enforce_api_rate_limit(request)
    result = await run_in_threadpool(market_service.fetch_market_price, commodity, state, mandi)
    if result is None:
        raise HTTPException(status_code=404, detail="No verified mandi quote is available for this crop and state right now.")
    return {"result": result.model_dump()}


@router.get("/api/advisory")
async def crop_advisory(request: Request, crop: str, nitrogen: float, phosphorus: float, potassium: float, ph: float, latitude: float | None = None, longitude: float | None = None):
    enforce_api_rate_limit(request)
    if (latitude is None) != (longitude is None) or (latitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180)):
        raise HTTPException(status_code=422, detail="Provide both valid latitude and longitude, or leave both blank.")
    try:
        weather = await advisory_service.fetch_weather(latitude, longitude)
        return {"result": advisory_service.build_advisory(crop, nitrogen, phosphorus, potassium, ph, weather)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
