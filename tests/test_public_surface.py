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
        self.assertIn("https://wa.me/14155238886", home.text)
        self.assertIn("व्यक्तिगत सलाह के लिए अनुरोध", home.text)
        self.assertIn('/static/i18n.js?v=4', home.text)
        business_css = self.client.get("/static/business.css")
        self.assertEqual(business_css.status_code, 200)
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


if __name__ == "__main__":
    unittest.main()
