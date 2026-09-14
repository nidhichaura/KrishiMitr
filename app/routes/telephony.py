"""SMS and keypad-phone (IVR) fallbacks for farmers without smartphones.

WhatsApp is for smartphones.  A basic 2G/3G phone can instead text a question
to the KrishiMitr number or call it and choose a menu option using its keypad.
Twilio sends both events to these public HTTPS webhook endpoints.
"""
from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.routes.webhook import route_incoming_message_with_language, verify_twilio_request

router = APIRouter()


def xml_response(twiml: object) -> Response:
    return Response(
        content=str(twiml).encode("utf-8"),
        headers={"Content-Type": "application/xml; charset=utf-8"},
    )


@router.post("/webhook/sms")
async def sms_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
):
    """Reply to a normal SMS using the same text-intent logic as WhatsApp."""
    await verify_twilio_request(request)
    response_text, _ = await route_incoming_message_with_language(Body, 0, None, None)
    twiml = MessagingResponse()
    twiml.message(response_text)
    return xml_response(twiml)


@router.post("/webhook/ivr")
async def ivr_welcome(request: Request):
    """Present a Hindi DTMF menu that works on a basic keypad phone."""
    await verify_twilio_request(request)
    twiml = VoiceResponse()
    gather = Gather(num_digits=1, action="/webhook/ivr/menu", method="POST", timeout=7)
    gather.say(
        "नमस्ते। आप कृषि मित्र पर हैं। मंडी भाव की एस एम एस जानकारी के लिए 1 दबाएं। "
        "फसल रोग सहायता के लिए 2 दबाएं। व्हाट्सऐप सहायता के लिए 3 दबाएं।",
        language="hi-IN",
    )
    twiml.append(gather)
    twiml.say("हमें कोई विकल्प नहीं मिला। कृपया फिर कॉल करें।", language="hi-IN")
    return xml_response(twiml)


@router.post("/webhook/ivr/menu")
async def ivr_menu(request: Request, Digits: str = Form("")):
    await verify_twilio_request(request)
    messages = {
        "1": (
            "मंडी भाव पाने के लिए हमारे नंबर पर एस एम एस करें। उदाहरण: भाव गेहूं उत्तर प्रदेश। "
            "आपको उपलब्ध ताजा जानकारी का उत्तर एस एम एस में मिलेगा।"
        ),
        "2": (
            "पत्ते की फोटो जांचने के लिए स्मार्टफोन से कृषि मित्र व्हाट्सऐप नंबर पर साफ फोटो भेजें। "
            "कीपैड फोन पर आप एस एम एस में अपनी फसल और बीमारी के लक्षण लिखकर सामान्य सलाह ले सकते हैं।"
        ),
        "3": "स्मार्टफोन में कृषि मित्र के व्हाट्सऐप नंबर पर नमस्ते लिखें। वहां आप संदेश, आवाज़ और पत्ते की फोटो भेज सकते हैं।",
    }
    twiml = VoiceResponse()
    twiml.say(messages.get(Digits, "गलत विकल्प। कृपया फिर कॉल करें और 1, 2, या 3 दबाएं।"), language="hi-IN")
    twiml.hangup()
    return xml_response(twiml)
