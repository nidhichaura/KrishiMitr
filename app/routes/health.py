"""
Simple health-check endpoint for uptime monitors / load balancers.
"""
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "KrishiMitr Backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
