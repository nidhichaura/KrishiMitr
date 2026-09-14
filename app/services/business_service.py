"""Consent, pilot metrics and privacy-preserving aggregate insights.

This module deliberately does not sell identifiable farmer records. Partner
reports only return grouped counts after a minimum cohort threshold is met.
"""
from __future__ import annotations

from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import sqlite3

from app.config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _identifier(value: str) -> str:
    """Keep a stable pseudonymous identifier instead of a phone/email value."""
    return sha256(value.strip().casefold().encode("utf-8")).hexdigest()


def _connect() -> sqlite3.Connection:
    path = Path(settings.BUSINESS_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise() -> None:
    with closing(_connect()) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            farmer_id TEXT PRIMARY KEY,
            state TEXT,
            district TEXT,
            preferred_language TEXT,
            consent_insights INTEGER NOT NULL DEFAULT 0,
            consent_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS plan_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id TEXT NOT NULL REFERENCES farmer_profiles(farmer_id),
            plan TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'requested',
            requested_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pilot_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id TEXT NOT NULL REFERENCES farmer_profiles(farmer_id),
            event_type TEXT NOT NULL,
            crop TEXT,
            state TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS marketplace_bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_type TEXT NOT NULL CHECK(trade_type IN ('buy','sell')),
            crop TEXT NOT NULL, quantity REAL NOT NULL, price REAL NOT NULL,
            location_label TEXT NOT NULL, latitude REAL, longitude REAL,
            bid_date TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)
        conn.commit()


def create_marketplace_bid(*, trade_type: str, crop: str, quantity: float, price: float,
                           location_label: str, bid_date: str, latitude: float | None = None,
                           longitude: float | None = None) -> dict:
    initialise()
    with closing(_connect()) as conn:
        cursor = conn.execute("""INSERT INTO marketplace_bids
          (trade_type,crop,quantity,price,location_label,latitude,longitude,bid_date,created_at)
          VALUES (?,?,?,?,?,?,?,?,?)""", (trade_type, crop, quantity, price, location_label, latitude, longitude, bid_date, _now()))
        conn.commit()
        return {"id": cursor.lastrowid}


def list_marketplace_bids(*, trade_type: str | None = None, limit: int = 30) -> list[dict]:
    initialise()
    query = "SELECT id,trade_type,crop,quantity,price,location_label,latitude,longitude,bid_date,created_at FROM marketplace_bids"
    values: list[object] = []
    if trade_type:
        query += " WHERE trade_type=?"; values.append(trade_type)
    query += " ORDER BY id DESC LIMIT ?"; values.append(min(max(limit, 1), 100))
    with closing(_connect()) as conn:
        return [dict(row) for row in conn.execute(query, values).fetchall()]


def save_profile(identifier: str, *, state: str | None, district: str | None,
                 preferred_language: str | None, consent_insights: bool) -> dict:
    initialise()
    farmer_id = _identifier(identifier)
    now = _now()
    with closing(_connect()) as conn:
        conn.execute("""
            INSERT INTO farmer_profiles
              (farmer_id, state, district, preferred_language, consent_insights, consent_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(farmer_id) DO UPDATE SET
              state=excluded.state, district=excluded.district,
              preferred_language=excluded.preferred_language,
              consent_insights=excluded.consent_insights,
              consent_at=excluded.consent_at, updated_at=excluded.updated_at
        """, (farmer_id, state, district, preferred_language, int(consent_insights),
              now if consent_insights else None, now, now))
        conn.commit()
    return {"farmer_id": farmer_id, "consent_insights": consent_insights}


def request_plan(identifier: str, plan: str) -> dict:
    if plan != "personalized_advisory":
        raise ValueError("Unsupported plan.")
    initialise()
    farmer_id = _identifier(identifier)
    now = _now()
    with closing(_connect()) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO farmer_profiles
              (farmer_id, consent_insights, created_at, updated_at)
            VALUES (?, 0, ?, ?)
        """, (farmer_id, now, now))
        conn.execute("INSERT INTO plan_requests (farmer_id, plan, requested_at) VALUES (?, ?, ?)",
                     (farmer_id, plan, now))
        conn.commit()
    return {"plan": plan, "status": "requested"}


def record_event(identifier: str, *, event_type: str, crop: str | None = None,
                 state: str | None = None) -> None:
    """Record only opted-in events; no raw phone number or message body is saved."""
    farmer_id = _identifier(identifier)
    initialise()
    with closing(_connect()) as conn:
        row = conn.execute("SELECT consent_insights FROM farmer_profiles WHERE farmer_id=?", (farmer_id,)).fetchone()
        if not row or not row["consent_insights"]:
            return
        conn.execute("INSERT INTO pilot_events (farmer_id, event_type, crop, state, created_at) VALUES (?, ?, ?, ?, ?)",
                     (farmer_id, event_type, crop, state, _now()))
        conn.commit()


def aggregate_insights() -> dict:
    """Return non-identifying partner metrics only if the cohort is large enough."""
    initialise()
    with closing(_connect()) as conn:
        farmer_count = conn.execute("SELECT COUNT(*) AS n FROM farmer_profiles WHERE consent_insights=1").fetchone()["n"]
        if farmer_count < settings.INSIGHTS_MINIMUM_COHORT:
            return {"available": False, "reason": "minimum_cohort_not_reached", "minimum_cohort": settings.INSIGHTS_MINIMUM_COHORT}
        rows = conn.execute("SELECT event_type, crop, state FROM pilot_events").fetchall()
    return {
        "available": True,
        "consented_farmer_count": farmer_count,
        "event_counts": dict(Counter(row["event_type"] for row in rows)),
        "crop_counts": dict(Counter(row["crop"] for row in rows if row["crop"])),
        "state_counts": dict(Counter(row["state"] for row in rows if row["state"])),
        "privacy": "Aggregated counts only; identifiers, phone numbers and message contents are excluded.",
    }
