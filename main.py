"""
KrishiMitr Backend — Application Entrypoint.

Run locally with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then expose it publicly (e.g. via ngrok) and set the resulting URL
(https://<your-domain>/webhook/whatsapp) as your Twilio WhatsApp Sandbox's
"WHEN A MESSAGE COMES IN" webhook.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import webhook, health, exotel_ivr
from app.routes import web, business
from app.services import vision_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="KrishiMitr Backend",
    description="Multilingual, voice-first AI assistant backend for Indian farmers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twilio downloads generated spoken replies from this public path.
from app.services.voice_reply_service import VOICE_REPLY_DIR
app.mount("/audio-replies", StaticFiles(directory=str(VOICE_REPLY_DIR)), name="audio-replies")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health.router, tags=["Health"])
app.include_router(webhook.router, tags=["WhatsApp Webhook"])
app.include_router(exotel_ivr.router, tags=["Exotel IVR"])
app.include_router(web.router, tags=["Farmer Web App"])
app.include_router(business.router)


@app.on_event("startup")
async def on_startup():
    logger.info(f"🌾 KrishiMitr backend starting up | env={settings.APP_ENV}")
    logger.info(f"Twilio WhatsApp sender number: {settings.TWILIO_WHATSAPP_NUMBER}")
    vision_service.warm_image_safety_model()


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🌾 KrishiMitr backend shutting down")
