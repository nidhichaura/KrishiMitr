"""Contract tests for Exotel IVR callback endpoints."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.schemas import MarketPriceResult
from main import app


class ExotelIvrTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_start_returns_language_gather(self):
        response = self.client.get("/webhook/exotel/ivr/start?callsid=demo-call")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<Gather", response.text)
        self.assertIn("अंग्रेज़ी के लिए 1", response.text)

    def test_state_transcript_is_normalized(self):
        response = self.client.post("/webhook/exotel/ivr/state", data={
            "callsid": "call-1", "transcript": "उत्तर प्रदेश", "language": "hi",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Uttar Pradesh", response.text)

    def test_crop_transcript_speaks_verified_quote(self):
        quote = MarketPriceResult(
            commodity="Wheat", state="Uttar Pradesh", mandi="Demo Mandi",
            min_price_per_quintal=2100, modal_price_per_quintal=2300,
            max_price_per_quintal=2500, price_date="2026-09-15",
        )
        with patch("app.routes.exotel_ivr.market_service.fetch_market_price", return_value=quote):
            self.client.post("/webhook/exotel/ivr/state", data={
                "callsid": "call-1", "transcript": "उत्तर प्रदेश", "language": "hi",
            })
            response = self.client.get(
                "/webhook/exotel/ivr/crop?callsid=call-1&transcript=गेहूं"
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("2300", response.text)


if __name__ == "__main__":
    unittest.main()
