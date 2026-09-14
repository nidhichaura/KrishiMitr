"""Pilot-facing APIs for consent, premium interest and partner aggregates."""
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings
from app.services import business_service

router = APIRouter(prefix="/api", tags=["Business Pilot"])


class FarmerProfileInput(BaseModel):
    identifier: str = Field(min_length=3, description="Phone/email used only to derive a one-way identifier.")
    state: str | None = None
    district: str | None = None
    preferred_language: str | None = None
    consent_insights: bool = False


class PlanRequestInput(BaseModel):
    identifier: str = Field(min_length=3)
    plan: str = "personalized_advisory"


class MarketplaceBidInput(BaseModel):
    trade_type: str = Field(pattern="^(buy|sell)$")
    crop: str = Field(min_length=2, max_length=60)
    quantity: float = Field(gt=0, le=100000)
    price: float = Field(gt=0, le=1000000)
    location_label: str = Field(min_length=2, max_length=160)
    bid_date: str = Field(min_length=10, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


def _require_partner_token(authorization: str | None) -> None:
    if not settings.PARTNER_API_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Partner reporting is not configured.")
    if authorization != f"Bearer {settings.PARTNER_API_TOKEN}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid partner credential.")


@router.post("/marketplace/bids", status_code=status.HTTP_201_CREATED)
async def create_marketplace_bid(payload: MarketplaceBidInput):
    return business_service.create_marketplace_bid(**payload.model_dump())


@router.get("/marketplace/bids")
async def marketplace_bids(trade_type: str | None = None):
    if trade_type not in (None, "buy", "sell"):
        raise HTTPException(status_code=422, detail="trade_type must be buy or sell")
    return {"bids": business_service.list_marketplace_bids(trade_type=trade_type)}


@router.post("/farmers/profile", status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(payload: FarmerProfileInput):
    """Save pilot profile fields and explicit consent choice."""
    return business_service.save_profile(payload.identifier, state=payload.state, district=payload.district,
                                         preferred_language=payload.preferred_language,
                                         consent_insights=payload.consent_insights)


@router.post("/plans/request", status_code=status.HTTP_202_ACCEPTED)
async def create_plan_request(payload: PlanRequestInput):
    """Capture interest only; payment/activation needs an external payment provider."""
    try:
        return business_service.request_plan(payload.identifier, payload.plan)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/partner/insights")
async def partner_insights(authorization: str | None = Header(default=None)):
    """B2G/B2B pilot view; never returns a farmer-level record."""
    _require_partner_token(authorization)
    return business_service.aggregate_insights()
