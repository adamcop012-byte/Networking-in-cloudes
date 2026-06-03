"""
WMS Service — Warehouse Management System
==========================================
Handles: warehouse locations, stock movements, dispatch queue.
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

app = FastAPI(title="WMS Service", version="1.0.0")

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# ── Simulated data store ───────────────────────────────────────────────────────
_WAREHOUSES = [
    {"id": "WH-01", "name": "Tashkent Central",  "city": "Tashkent",  "capacity": 5000, "used": 3240, "country": "UZ"},
    {"id": "WH-02", "name": "Samarkand Depot",   "city": "Samarkand", "capacity": 2000, "used": 980,  "country": "UZ"},
    {"id": "WH-03", "name": "Almaty Hub",         "city": "Almaty",    "capacity": 3000, "used": 2100, "country": "KZ"},
]

_STOCK_MOVEMENTS = [
    {"id": "MOV-001", "type": "inbound",  "product": "P001", "qty": 500, "warehouse": "WH-01", "date": "2026-05-18"},
    {"id": "MOV-002", "type": "outbound", "product": "P002", "qty": 200, "warehouse": "WH-01", "date": "2026-05-19"},
    {"id": "MOV-003", "type": "transfer", "product": "P003", "qty": 100, "warehouse": "WH-02", "date": "2026-05-20"},
    {"id": "MOV-004", "type": "outbound", "product": "P001", "qty": 50,  "warehouse": "WH-03", "date": "2026-05-21"},
]

_DISPATCH_QUEUE = [
    {"order_id": "ORD-1001", "warehouse": "WH-01", "priority": "high",   "status": "picked",   "items": 50},
    {"order_id": "ORD-1002", "warehouse": "WH-02", "priority": "normal", "status": "packing",  "items": 100},
    {"order_id": "ORD-1004", "warehouse": "WH-01", "priority": "urgent", "status": "awaiting", "items": 25},
]

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "service": "WMS",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subnet": "private-subnet-a",
        "version": "1.0.0",
    }

@app.get("/api/warehouses")
async def get_warehouses() -> dict[str, Any]:
    for wh in _WAREHOUSES:
        wh["utilisation_pct"] = round(wh["used"] / wh["capacity"] * 100, 1)
    return {
        "service": "WMS",
        "total_warehouses": len(_WAREHOUSES),
        "total_capacity": sum(w["capacity"] for w in _WAREHOUSES),
        "total_used": sum(w["used"] for w in _WAREHOUSES),
        "warehouses": _WAREHOUSES,
    }

@app.get("/api/warehouses/{warehouse_id}")
async def get_warehouse(warehouse_id: str) -> dict[str, Any]:
    wh = next((w for w in _WAREHOUSES if w["id"] == warehouse_id), None)
    if not wh:
        raise HTTPException(status_code=404, detail=f"Warehouse {warehouse_id} not found")
    return {**wh, "utilisation_pct": round(wh["used"] / wh["capacity"] * 100, 1)}

@app.get("/api/stock-movements")
async def get_stock_movements() -> dict[str, Any]:
    return {
        "service": "WMS",
        "movements": _STOCK_MOVEMENTS,
        "summary": {
            "inbound":  sum(m["qty"] for m in _STOCK_MOVEMENTS if m["type"] == "inbound"),
            "outbound": sum(m["qty"] for m in _STOCK_MOVEMENTS if m["type"] == "outbound"),
            "transfer": sum(m["qty"] for m in _STOCK_MOVEMENTS if m["type"] == "transfer"),
        },
    }

@app.get("/api/dispatch")
async def get_dispatch_queue() -> dict[str, Any]:
    return {
        "service": "WMS",
        "queue": _DISPATCH_QUEUE,
        "urgent": [d for d in _DISPATCH_QUEUE if d["priority"] == "urgent"],
        "total_items_queued": sum(d["items"] for d in _DISPATCH_QUEUE),
    }

@app.get("/api/stats")
async def stats() -> dict[str, Any]:
    total_cap = sum(w["capacity"] for w in _WAREHOUSES)
    total_used = sum(w["used"] for w in _WAREHOUSES)
    return {
        "service": "WMS",
        "warehouses": len(_WAREHOUSES),
        "total_capacity": total_cap,
        "total_used": total_used,
        "overall_utilisation_pct": round(total_used / total_cap * 100, 1),
        "dispatch_queue_length": len(_DISPATCH_QUEUE),
        "stock_movements_today": len(_STOCK_MOVEMENTS),
    }
