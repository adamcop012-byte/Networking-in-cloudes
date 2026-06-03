"""
CRM Service — Customer Relationship Management
===============================================
Handles: customers, contacts, sales pipeline, activity log.
Runs in PRIVATE subnet — accessed only through the API Gateway.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CRM Service", version="1.0.0")

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# ── Simulated data store ───────────────────────────────────────────────────────
_CUSTOMERS = [
    {"id": "C001", "name": "Tashkent Retail Co.",     "country": "UZ", "tier": "gold",   "orders": 18, "lifetime_value": 42800},
    {"id": "C002", "name": "Almaty Fashion Hub",       "country": "KZ", "tier": "silver", "orders": 9,  "lifetime_value": 18600},
    {"id": "C003", "name": "Istanbul Wholesale Ltd.",  "country": "TR", "tier": "gold",   "orders": 31, "lifetime_value": 87500},
    {"id": "C004", "name": "Bishkek Garments",         "country": "KG", "tier": "bronze", "orders": 4,  "lifetime_value": 6200},
    {"id": "C005", "name": "Dushanbe Traders",         "country": "TJ", "tier": "silver", "orders": 12, "lifetime_value": 24100},
]

_PIPELINE = [
    {"id": "DEAL-01", "customer": "C001", "value": 15000, "stage": "proposal",    "probability": 70},
    {"id": "DEAL-02", "customer": "C003", "value": 32000, "stage": "negotiation", "probability": 85},
    {"id": "DEAL-03", "customer": "C005", "value": 8500,  "stage": "prospect",    "probability": 40},
    {"id": "DEAL-04", "customer": "C002", "value": 11000, "stage": "closed_won",  "probability": 100},
]

_ACTIVITY = [
    {"type": "call",    "customer": "C001", "note": "Discussed Q3 bulk order",          "date": "2026-05-20"},
    {"type": "email",   "customer": "C003", "note": "Sent winter catalogue",             "date": "2026-05-21"},
    {"type": "meeting", "customer": "C002", "note": "On-site visit — warehouse review",  "date": "2026-05-22"},
]

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "service": "CRM",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subnet": "private-subnet-b",
        "version": "1.0.0",
    }

@app.get("/api/customers")
async def get_customers() -> dict[str, Any]:
    return {
        "service": "CRM",
        "total_customers": len(_CUSTOMERS),
        "customers": _CUSTOMERS,
        "summary": {
            "gold":   sum(1 for c in _CUSTOMERS if c["tier"] == "gold"),
            "silver": sum(1 for c in _CUSTOMERS if c["tier"] == "silver"),
            "bronze": sum(1 for c in _CUSTOMERS if c["tier"] == "bronze"),
        },
    }

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str) -> dict[str, Any]:
    customer = next((c for c in _CUSTOMERS if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer

@app.get("/api/pipeline")
async def get_pipeline() -> dict[str, Any]:
    total_weighted = sum(d["value"] * d["probability"] / 100 for d in _PIPELINE)
    return {
        "service": "CRM",
        "deals": _PIPELINE,
        "total_pipeline_value": sum(d["value"] for d in _PIPELINE),
        "weighted_value": round(total_weighted, 2),
    }

@app.get("/api/activity")
async def get_activity() -> dict[str, Any]:
    return {
        "service": "CRM",
        "recent_activities": _ACTIVITY,
        "count": len(_ACTIVITY),
    }

@app.get("/api/stats")
async def stats() -> dict[str, Any]:
    return {
        "service": "CRM",
        "total_customers": len(_CUSTOMERS),
        "total_lifetime_value": sum(c["lifetime_value"] for c in _CUSTOMERS),
        "active_deals": len([d for d in _PIPELINE if d["stage"] != "closed_won"]),
        "pipeline_value": sum(d["value"] for d in _PIPELINE),
    }
