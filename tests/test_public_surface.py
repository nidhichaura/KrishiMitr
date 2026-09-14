"""Smoke tests for the farmer website and security boundaries."""
import unittest

from fastapi.testclient import TestClient

from app.config import settings
from main import app


class PublicSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_farmer_home_and_health_are_available(self):
        home = self.client.get("/")
        health = self.client.get("/health")
        self.assertEqual(home.status_code, 200)
        self.assertIn("KrishiMitr", home.text)
        self.assertEqual(health.json()["status"], "ok")

    def test_forged_webhook_is_rejected_when_verification_is_enabled(self):
        original = settings.VERIFY_TWILIO_SIGNATURES
        settings.VERIFY_TWILIO_SIGNATURES = True
        try:
            response = self.client.post("/webhook/whatsapp", data={
                "From": "whatsapp:+919876543210", "To": "whatsapp:+14155238886",
                "Body": "namaste", "NumMedia": "0",
            })
        finally:
            settings.VERIFY_TWILIO_SIGNATURES = original
        self.assertEqual(response.status_code, 403)

    def test_public_photo_api_rejects_non_images(self):
        response = self.client.post(
            "/api/disease/analyze",
            files={"image": ("unsafe.txt", b"not an image", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)

    def test_keypad_phone_ivr_returns_a_hindi_menu(self):
        original = settings.VERIFY_TWILIO_SIGNATURES
        settings.VERIFY_TWILIO_SIGNATURES = False
        try:
            response = self.client.post("/webhook/ivr")
        finally:
            settings.VERIFY_TWILIO_SIGNATURES = original
        self.assertEqual(response.status_code, 200)
        self.assertIn("<Gather", response.text)
        self.assertIn("मंडी भाव", response.text)


if __name__ == "__main__":
    unittest.main()
