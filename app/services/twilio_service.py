"""
Twilio integration service.

Two delivery mechanisms are supported (both are "the Twilio WhatsApp API"):

1. TwiML reply (used in the webhook route) — the fast, synchronous path.
   Twilio POSTs the inbound message to our webhook and expects an XML
   <Response> back within a few seconds; Twilio then relays that message
   to the farmer. This is what `app/routes/webhook.py` uses for the main flow.

2. REST API push (this service's `send_whatsapp_message`) — used for
   proactive / out-of-band messages, e.g. a background job that notifies a
   farmer their disease-check result is ready, or a scheduled market-price
   alert broadcast. This requires the Account SID + Auth Token and is a
   normal outbound HTTP call independent of any inbound webhook.
"""
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_whatsapp_message(self, to_number: str, body: str, media_url: Optional[str] = None) -> str:
        """
        Proactively push a WhatsApp message via the Twilio REST API.
        `to_number` must be in the form 'whatsapp:+91XXXXXXXXXX'.
        Returns the Twilio Message SID on success.
        """
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        kwargs = {
            "from_": self.from_number,
            "to": to_number,
            "body": body,
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        try:
            message = self.client.messages.create(**kwargs)
            logger.info(f"Sent WhatsApp message to {to_number} (SID={message.sid})")
            return message.sid
        except TwilioRestException as exc:
            logger.error(f"Twilio REST API error sending to {to_number}: {exc}")
            raise


# Singleton so the Twilio HTTP client isn't re-created on every call
_twilio_service_instance: Optional[TwilioService] = None


def get_twilio_service() -> TwilioService:
    global _twilio_service_instance
    if _twilio_service_instance is None:
        _twilio_service_instance = TwilioService()
    return _twilio_service_instance
