"""Tests for the consent-first B2G/B2B and freemium pilot foundation."""
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.config import settings
from main import app


class BusinessPilotTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db = settings.BUSINESS_DB_PATH
        self.original_token = settings.PARTNER_API_TOKEN
        self.original_cohort = settings.INSIGHTS_MINIMUM_COHORT
        settings.BUSINESS_DB_PATH = os.path.join(self.tempdir.name, "pilot.db")
        settings.PARTNER_API_TOKEN = "test-partner-token"
        settings.INSIGHTS_MINIMUM_COHORT = 1

    def tearDown(self):
        settings.BUSINESS_DB_PATH = self.original_db
        settings.PARTNER_API_TOKEN = self.original_token
        settings.INSIGHTS_MINIMUM_COHORT = self.original_cohort
        self.tempdir.cleanup()

    def test_profile_and_premium_interest_are_recorded_without_raw_identifier_output(self):
        profile = self.client.post("/api/farmers/profile", json={
            "identifier": "+919876543210", "state": "Punjab", "consent_insights": True,
        })
        self.assertEqual(profile.status_code, 201)
        self.assertNotIn("+919876543210", profile.text)
        plan = self.client.post("/api/plans/request", json={"identifier": "+919876543210"})
        self.assertEqual(plan.status_code, 202)
        self.assertEqual(plan.json()["status"], "requested")

    def test_partner_view_requires_token_and_returns_only_aggregates(self):
        self.client.post("/api/farmers/profile", json={"identifier": "farmer@example.com", "consent_insights": True})
        denied = self.client.get("/api/partner/insights")
        allowed = self.client.get("/api/partner/insights", headers={"Authorization": "Bearer test-partner-token"})
        self.assertEqual(denied.status_code, 401)
        self.assertEqual(allowed.status_code, 200)
        self.assertTrue(allowed.json()["available"])
        self.assertNotIn("farmer@example.com", allowed.text)
