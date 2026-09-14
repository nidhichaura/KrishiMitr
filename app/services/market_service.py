"""Verified mandi-price lookup using the Government of India OGD/AGMARKNET API.

This module deliberately never fabricates a price.  If the official feed is
not configured, unavailable, or has no matching market record, it returns
``None`` and the farmer is told that a verified quote is unavailable.
"""
from datetime import date, timedelta
from functools import lru_cache
from typing import Any

import httpx

from app.config import settings
from app.models.schemas import MarketPriceResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

# The conversational crop labels differ from the official AGMARKNET labels.
# Query with the source's canonical commodity spelling, not the user's words.
_AGMARKNET_COMMODITIES = {
    "rice": "Paddy(Dhan)",
    "soybean": "Soyabean",
}

_AGMARKNET_2_COMMODITIES = {
    "rice": "Rice", "wheat": "Wheat", "cotton": "Cotton", "onion": "Onion",
    "tomato": "Tomato", "potato": "Potato", "soybean": "Soyabean",
    "sugarcane": "Sugarcane", "maize": "Maize", "mustard": "Mustard",
    "apple": "Apple", "banana": "Banana", "bhindi": "Bhindi(Ladies Finger)",
    "bottle gourd": "Bottle gourd", "brinjal": "Brinjal", "cauliflower": "Cauliflower",
    "cucumber": "Cucumbar(Kheera)", "lemon": "Lemon", "papaya": "Papaya",
    "pumpkin": "Pumpkin", "radish": "Raddish", "sponge gourd": "Sponge gourd",
}
_AGMARKNET_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/",
    "User-Agent": "KrishiMitr/1.0 (+https://agmarknet.gov.in)",
}


def _recent_state_report(state: str) -> tuple[list[dict[str, Any]], date] | None:
    """Return today's report, or the most recent published official report.

    AGMARKNET does not publish every calendar day (notably before its morning
    update, on Sundays, and on holidays). The returned date stays attached to
    the quote, so this fallback never presents an older verified price as new.
    """
    try:
        state_id = _agmarknet_states()[state.casefold()]
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        logger.warning("Agmarknet state lookup failed: %s", exc)
        return None

    for days_ago in range(7):
        report_date = date.today() - timedelta(days=days_ago)
        try:
            response = httpx.get(
                f"{settings.AGMARKNET_API_URL.rstrip('/')}/prices-and-arrivals/commodity-market/daily-report-state",
                params={"date": report_date.isoformat(), "state": state_id, "includeExcel": "false"},
                headers=_AGMARKNET_HEADERS,
                timeout=httpx.Timeout(12.0, connect=5.0),
            )
            response.raise_for_status()
            groups = response.json().get("commodityGroups", [])
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            logger.warning("Agmarknet report lookup failed for %s: %s", report_date, exc)
            return None
        if groups:
            if days_ago:
                logger.info("Using latest published Agmarknet report from %s for %s", report_date, state)
            return groups, report_date
    return None

def _number(record: dict[str, Any], field: str) -> float:
    """Read OGD numeric fields which may be returned as strings."""
    return float(str(record[field]).replace(",", "").strip())


@lru_cache(maxsize=1)
def _agmarknet_states() -> dict[str, int]:
    """Get the official Agmarknet 2.0 state IDs and cache them in memory."""
    response = httpx.get(
        f"{settings.AGMARKNET_API_URL.rstrip('/')}/daily-price-arrival/filters",
        headers=_AGMARKNET_HEADERS,
        timeout=httpx.Timeout(12.0, connect=5.0),
    )
    response.raise_for_status()
    states = response.json()["data"]["state_data"]
    return {str(item["state_name"]).casefold(): int(item["state_id"]) for item in states}


def _fetch_agmarknet_2_price(
    commodity: str, state: str, mandi: str | None = None
) -> MarketPriceResult | None:
    """Read the current official state report from Agmarknet 2.0.

    Unlike the older data.gov.in mirror, this endpoint is the live public
    backend behind Agmarknet's current portal. It returns all crops reported
    by the requested state for the day, from which we select the farmer's
    crop and optionally the named mandi.
    """
    wanted_commodity = _AGMARKNET_2_COMMODITIES.get(commodity.lower().strip(), commodity.strip())
    report = _recent_state_report(state)
    if report is None:
        return None
    groups, report_date = report

    wanted = wanted_commodity.casefold()
    for group in groups:
        for crop in group.get("commodities", []):
            if str(crop.get("commodityName", "")).casefold() != wanted:
                continue
            markets = crop.get("markets", [])
            if mandi:
                markets = [item for item in markets if mandi.casefold() in str(item.get("marketCenter", "")).casefold()]
            for market in markets:
                rows = market.get("data") or []
                if not rows:
                    continue
                row = rows[0]
                try:
                    return MarketPriceResult(
                        commodity=str(crop["commodityName"]),
                        state=state,
                        mandi=str(market["marketCenter"]),
                        min_price_per_quintal=_number(row, "minimumPrice"),
                        max_price_per_quintal=_number(row, "maximumPrice"),
                        modal_price_per_quintal=_number(row, "modalPrice"),
                        price_date=report_date.isoformat(),
                        variety=row.get("variety"),
                        source="AGMARKNET 2.0 (Ministry of Agriculture)",
                    )
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning("Unexpected Agmarknet 2.0 market record: %s", exc)
    return None


def list_available_commodities(state: str) -> list[str] | None:
    """Return crops reported by the selected state in today's official feed.

    This is useful in a live demo: the user can see exactly which crops have
    a report before requesting a price, instead of guessing.
    """
    report = _recent_state_report(state)
    if report is None:
        return None
    groups, _ = report
    try:
        commodities = {
            str(crop["commodityName"]).strip()
            for group in groups for crop in group.get("commodities", [])
            if crop.get("commodityName") and crop.get("markets")
        }
        return sorted(commodities, key=str.casefold)
    except (KeyError, TypeError, ValueError) as exc:
        logger.warning("Agmarknet 2.0 commodity-list lookup failed: %s", exc)
        return None


def fetch_market_price(
    commodity: str, state: str | None = None, mandi: str | None = None
) -> MarketPriceResult | None:
    """Return the newest official wholesale quote for the requested location.

    ``state`` and ``mandi`` are optional filters.  When neither is supplied,
    callers should ask the farmer for a location instead of selecting an
    arbitrary market from another state.
    """
    # Agmarknet 2.0 is the primary source: it is public, current, and avoids
    # the intermittent timeout seen on the legacy data.gov.in mirror.
    if state:
        official_result = _fetch_agmarknet_2_price(commodity, state, mandi)
        if official_result is not None:
            return official_result

    if not settings.DATA_GOV_API_KEY:
        logger.error("Mandi lookup blocked: no Agmarknet result and DATA_GOV_API_KEY is not configured.")
        return None

    official_commodity = _AGMARKNET_COMMODITIES.get(commodity.lower().strip(), commodity.strip())
    params = {
        "api-key": settings.DATA_GOV_API_KEY,
        "format": "json",
        "limit": 10,
        "offset": 0,
        "filters[commodity]": official_commodity,
    }
    if state:
        params["filters[state]"] = state.strip()
    if mandi:
        params["filters[market]"] = mandi.strip()

    try:
        response = httpx.get(
            f"{settings.DATA_GOV_API_URL.rstrip('/')}/{settings.DATA_GOV_RESOURCE_ID}",
            params=params,
            # A webhook must answer Twilio promptly.  Fail safely instead of
            # allowing a slow government endpoint to make the user wait.
            timeout=httpx.Timeout(3.0, connect=2.0),
        )
        response.raise_for_status()
        records = response.json().get("records", [])
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("Official mandi lookup failed: %s", exc)
        return None

    if not records:
        logger.info("No official mandi quote for commodity=%s state=%s mandi=%s", commodity, state, mandi)
        return None

    # API responses are normally newest first.  The response still shows the
    # source's arrival date so stale data can never be mistaken for today's rate.
    record = records[0]
    try:
        return MarketPriceResult(
            commodity=record["commodity"],
            state=record["state"],
            mandi=record["market"],
            min_price_per_quintal=_number(record, "min_price"),
            max_price_per_quintal=_number(record, "max_price"),
            modal_price_per_quintal=_number(record, "modal_price"),
            price_date=record["arrival_date"],
            variety=record.get("variety"),
        )
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning("Unexpected official mandi record: %s", exc)
        return None
