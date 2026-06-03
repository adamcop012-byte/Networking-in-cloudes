"""
ERP Service — Enterprise Resource Planning
==========================================
Handles: orders, inventory, product catalogue with images.
In the cloud architecture this runs in the PRIVATE subnet —
only reachable through the Nginx API Gateway (public subnet).
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ERP Service", version="1.0.0")

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# ── Simulated data store ───────────────────────────────────────────────────────
# Images: picsum.photos — deterministic per seed, always loads, free
_PRODUCTS = [
    {
        "id": "P001",
        "name": "Men's Denim Jacket",
        "sku": "MDJ-001",
        "category": "Outerwear",
        "stock": 240,
        "price": 45.99,
        "image_url": "https://picsum.photos/seed/MDJ001/300/300",
        "supplier": "Tashkent Mills Co.",
        "reorder_level": 50,
    },
    {
        "id": "P002",
        "name": "Women's Silk Blouse",
        "sku": "WSB-002",
        "category": "Tops",
        "stock": 380,
        "price": 22.50,
        "image_url": "https://picsum.photos/seed/WSB002/300/300",
        "supplier": "Fergana Textile Ltd.",
        "reorder_level": 80,
    },
    {
        "id": "P003",
        "name": "Cargo Trousers",
        "sku": "CGT-003",
        "category": "Bottoms",
        "stock": 155,
        "price": 34.00,
        "image_url": "https://picsum.photos/seed/CGT003/300/300",
        "supplier": "Istanbul Garments",
        "reorder_level": 40,
    },
    {
        "id": "P004",
        "name": "Polo Shirt (6-pack)",
        "sku": "PSP-004",
        "category": "Tops",
        "stock": 90,
        "price": 68.00,
        "image_url": "https://picsum.photos/seed/PSP004/300/300",
        "supplier": "Samarkand Fabrics",
        "reorder_level": 30,
    },
    {
        "id": "P005",
        "name": "Winter Coat",
        "sku": "WCT-005",
        "category": "Outerwear",
        "stock": 60,
        "price": 89.99,
        "image_url": "https://picsum.photos/seed/WCT005/300/300",
        "supplier": "Almaty Fashion Hub",
        "reorder_level": 20,
    },
    {
        "id": "P006",
        "name": "Classic Hoodie",
        "sku": "CHD-006",
        "category": "Tops",
        "stock": 310,
        "price": 28.00,
        "image_url": "https://picsum.photos/seed/CHD006/300/300",
        "supplier": "Tashkent Mills Co.",
        "reorder_level": 60,
    },
    {
        "id": "P007",
        "name": "Slim-Fit Chinos",
        "sku": "SFC-007",
        "category": "Bottoms",
        "stock": 200,
        "price": 31.50,
        "image_url": "https://picsum.photos/seed/SFC007/300/300",
        "supplier": "Fergana Textile Ltd.",
        "reorder_level": 50,
    },
    {
        "id": "P008",
        "name": "Formal Dress Shirt",
        "sku": "FDS-008",
        "category": "Tops",
        "stock": 420,
        "price": 19.99,
        "image_url": "https://picsum.photos/seed/FDS008/300/300",
        "supplier": "Istanbul Garments",
        "reorder_level": 100,
    },
    {
        "id": "P009",
        "name": "Summer Linen Set",
        "sku": "SLS-009",
        "category": "Sets",
        "stock": 75,
        "price": 54.00,
        "image_url": "https://picsum.photos/seed/SLS009/300/300",
        "supplier": "Samarkand Fabrics",
        "reorder_level": 25,
    },
    {
        "id": "P010",
        "name": "Waterproof Windbreaker",
        "sku": "WWB-010",
        "category": "Outerwear",
        "stock": 130,
        "price": 72.00,
        "image_url": "https://picsum.photos/seed/WWB010/300/300",
        "supplier": "Almaty Fashion Hub",
        "reorder_level": 30,
    },
]

_ORDERS = [
    {"id": "ORD-1001", "customer": "C001", "product": "P001", "qty": 50,  "status": "shipped",    "total": 2299.50},
    {"id": "ORD-1002", "customer": "C002", "product": "P003", "qty": 100, "status": "processing", "total": 3400.00},
    {"id": "ORD-1003", "customer": "C003", "product": "P002", "qty": 200, "status": "delivered",  "total": 4500.00},
    {"id": "ORD-1004", "customer": "C004", "product": "P005", "qty": 25,  "status": "pending",    "total": 2249.75},
    {"id": "ORD-1005", "customer": "C005", "product": "P006", "qty": 150, "status": "shipped",    "total": 4200.00},
    {"id": "ORD-1006", "customer": "C001", "product": "P008", "qty": 300, "status": "delivered",  "total": 5997.00},
    {"id": "ORD-1007", "customer": "C003", "product": "P010", "qty": 40,  "status": "processing", "total": 2880.00},
]

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "service": "ERP",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subnet": "private-subnet-a",
        "version": "1.0.0",
    }


@app.get("/api/inventory")
async def get_inventory() -> dict[str, Any]:
    low_stock = [p for p in _PRODUCTS if p["stock"] <= p["reorder_level"]]
    return {
        "service": "ERP",
        "total_products": len(_PRODUCTS),
        "total_stock_units": sum(p["stock"] for p in _PRODUCTS),
        "low_stock_alerts": len(low_stock),
        "products": _PRODUCTS,
    }


@app.get("/api/inventory/{product_id}")
async def get_product(product_id: str) -> dict[str, Any]:
    product = next((p for p in _PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@app.get("/api/catalogue")
async def get_catalogue() -> dict[str, Any]:
    """
    Product catalogue — returns all products with image URLs.
    Used by the dashboard to render a visual product grid.
    """
    categories = {}
    for p in _PRODUCTS:
        cat = p["category"]
        categories.setdefault(cat, 0)
        categories[cat] += 1

    return {
        "service": "ERP",
        "total_products": len(_PRODUCTS),
        "categories": categories,
        "catalogue": [
            {
                "id": p["id"],
                "name": p["name"],
                "sku": p["sku"],
                "category": p["category"],
                "price": p["price"],
                "stock": p["stock"],
                "image_url": p["image_url"],
                "in_stock": p["stock"] > p["reorder_level"],
                "low_stock": 0 < p["stock"] <= p["reorder_level"],
            }
            for p in _PRODUCTS
        ],
    }


@app.get("/api/orders")
async def get_orders() -> dict[str, Any]:
    return {
        "service": "ERP",
        "orders_count": len(_ORDERS),
        "orders": _ORDERS,
    }


@app.get("/api/stats")
async def stats() -> dict[str, Any]:
    revenue = sum(o["total"] for o in _ORDERS)
    low_stock = [p for p in _PRODUCTS if p["stock"] <= p["reorder_level"]]
    return {
        "service": "ERP",
        "orders_count": len(_ORDERS),
        "revenue_total": round(revenue, 2),
        "products_total": len(_PRODUCTS),
        "low_stock_count": len(low_stock),
        "avg_order_value": round(revenue / len(_ORDERS), 2),
    }
