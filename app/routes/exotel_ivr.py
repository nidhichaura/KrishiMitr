"""Exotel-compatible IVR webhook for KrishiMitr.

The first menu uses DTMF (1/2/3), which works on every keypad phone. The
state and crop stages accept a transcript supplied by Exotel Voicebot or an
AgentStream bridge; plain ExoML IVR alone cannot reliably turn spoken Hindi
into text. See EXOTEL_IVR_SETUP.md for the corresponding Exotel Flow.
"""
from __future__ import annotations

from html import escape
from time import monotonic
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from app.config import settings
from app.services import market_service, speech_service
from app.utils.language_utils import detect_user_language

router = APIRouter()
_CALL_CONTEXT: dict[str, tuple[float, str, str]] = {}
_CONTEXT_TTL_SECONDS = 15 * 60


def _base_url(request: Request) -> str:
    return (settings.EXOTEL_PUBLIC_BASE_URL or str(request.base_url)).rstrip("/")


async def _value(request: Request, *names: str) -> str:
    """Read Exotel flow parameters across ExoML/Voicebot field spellings."""
    form = await request.form() if request.method == "POST" else {}
    for name in names:
        value = request.query_params.get(name) or form.get(name)
        if value:
            return str(value).strip().strip('"')
    return ""


async def _call_id(request: Request) -> str:
    return await _value(request, "CallSid", "callsid", "call_sid", "conversation_id") or "anonymous"


def _save_context(call_id: str, state: str, language: str) -> None:
    now = monotonic()
    for key, (created, _, _) in list(_CALL_CONTEXT.items()):
        if now - created > _CONTEXT_TTL_SECONDS:
            del _CALL_CONTEXT[key]
    _CALL_CONTEXT[call_id] = (now, state, language)


def _context(call_id: str) -> tuple[str, str]:
    stored = _CALL_CONTEXT.get(call_id)
    if not stored or monotonic() - stored[0] > _CONTEXT_TTL_SECONDS:
        return "", ""
    return stored[1], stored[2]


def _xml(say: str, *, gather_action: str | None = None, num_digits: int = 1) -> Response:
    """Return ExoML. Exotel's ExoML supports Say and Gather for DTMF IVR."""
    spoken = escape(say)
    if gather_action:
        body = (
            f'<Response><Gather action="{escape(gather_action, quote=True)}" '
            f'method="GET" numDigits="{num_digits}" timeout="8">'
            f'<Say language="hi-IN">{spoken}</Say></Gather>'
            '<Say language="hi-IN">कोई विकल्प नहीं मिला। कृपया फिर कॉल करें।</Say></Response>'
        )
    else:
        body = f'<Response><Say language="hi-IN">{spoken}</Say><Hangup/></Response>'
    return Response(content=body.encode("utf-8"), media_type="application/xml")


LANGUAGE_PROMPT = (
    "नमस्ते। कृषि मित्र में आपका स्वागत है। अंग्रेज़ी के लिए 1 दबाएँ। "
    "हिंदी के लिए 2 दबाएँ। अन्य भारतीय भाषा के लिए 3 दबाएँ।"
)


@router.api_route("/webhook/exotel/ivr/start", methods=["GET", "POST"])
async def start(request: Request):
    call_id = await _call_id(request)
    action = f"{_base_url(request)}/webhook/exotel/ivr/language?{urlencode({'call_id': call_id})}"
    return _xml(LANGUAGE_PROMPT, gather_action=action)


@router.api_route("/webhook/exotel/ivr/language", methods=["GET", "POST"])
async def language(request: Request):
    choice = await _value(request, "Digits", "digits", "digit")
    language = {"1": "en", "2": "hi", "3": "regional"}.get(choice)
    if not language:
        return _xml("कृपया 1, 2, या 3 दबाएँ।", gather_action=f"{_base_url(request)}/webhook/exotel/ivr/language")

    call_id = await _call_id(request)
    prompt = {
        "en": "Please say the state whose mandi price you want to know.",
        "hi": "कृपया उस राज्य का नाम बोलें जिसका मंडी भाव जानना चाहते हैं।",
        "regional": "कृपया अपनी भाषा में राज्य का नाम बोलें।",
    }[language]
    return _xml(prompt + " आपकी आवाज़ पहचानने के लिए कृषि मित्र वॉइस बॉट शुरू किया जा रहा है।")


@router.api_route("/webhook/exotel/ivr/state", methods=["GET", "POST"])
async def state(request: Request):
    transcript = await _value(request, "transcript", "speech", "SpeechResult", "utterance", "text")
    language = await _value(request, "language") or detect_user_language(transcript)
    state_name = speech_service.extract_state(transcript)
    if not state_name:
        return _xml("राज्य का नाम समझ नहीं आया। कृपया राज्य का नाम फिर से स्पष्ट बोलें।")
    call_id = await _call_id(request)
    _save_context(call_id, state_name, language)
    # The Exotel Flow's next Voicebot stage collects the crop name. Preserve
    # these values in that stage's custom parameters/callback URL.
    return _xml(f"आपने {state_name} चुना है। अब फसल का नाम बोलें।")


@router.api_route("/webhook/exotel/ivr/crop", methods=["GET", "POST"])
async def crop(request: Request):
    transcript = await _value(request, "transcript", "speech", "SpeechResult", "utterance", "text")
    call_id = await _call_id(request)
    state_name = await _value(request, "state")
    language = await _value(request, "language") or detect_user_language(transcript)
    saved_state, saved_language = _context(call_id)
    state_name = state_name or saved_state
    language = language or saved_language
    commodity = speech_service.extract_commodity(transcript)
    if not state_name or not commodity:
        return _xml("फसल का नाम स्पष्ट नहीं मिला। कृपया गेहूं, धान, मक्का जैसी फसल का नाम फिर से बोलें।")

    quote = await run_in_threadpool(market_service.fetch_market_price, commodity, state_name)
    if quote is None:
        return _xml(f"{commodity} के लिए {state_name} का सत्यापित मंडी भाव अभी उपलब्ध नहीं है।")
    message = (
        f"{quote.commodity}, {quote.mandi}, {quote.state} का मॉडल भाव "
        f"{round(quote.modal_price_per_quintal)} रुपये प्रति क्विंटल है। "
        f"न्यूनतम {round(quote.min_price_per_quintal)} और अधिकतम "
        f"{round(quote.max_price_per_quintal)} रुपये प्रति क्विंटल।"
    )
    return _xml(message)
