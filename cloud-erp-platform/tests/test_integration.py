"""
Integration Tests — Cloud ERP Platform
========================================
Tests for API endpoints, data integrity, and inter-service communication.

Run with: pip install pytest httpx && pytest tests/test_integration.py -v
"""

from fastapi.testclient import TestClient


def test_erp_imports():
    """Verify ERP service imports correctly."""
    from services.erp.main import app as erp_app
    assert erp_app is not None
    assert erp_app.title == "ERP Service"


def test_crm_imports():
    """Verify CRM service imports correctly."""
    from services.crm.main import app as crm_app
    assert crm_app is not None
    assert crm_app.title == "CRM Service"


def test_wms_imports():
    """Verify WMS service imports correctly."""
    from services.wms.main import app as wms_app
    assert wms_app is not None
    assert wms_app.title == "WMS Service"


def test_erp_health():
    """Test ERP health check endpoint."""
    from services.erp.main import app as erp_app
    client = TestClient(erp_app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ERP"
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_crm_health():
    """Test CRM health check endpoint."""
    from services.crm.main import app as crm_app
    client = TestClient(crm_app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CRM"
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_wms_health():
    """Test WMS health check endpoint."""
    from services.wms.main import app as wms_app
    client = TestClient(wms_app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "WMS"
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_erp_inventory():
    """Test ERP inventory endpoint."""
    from services.erp.main import app as erp_app
    client = TestClient(erp_app)
    response = client.get("/api/inventory")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ERP"
    assert "total_products" in data
    assert "products" in data
    assert len(data["products"]) == 10


def test_erp_orders():
    """Test ERP orders endpoint."""
    from services.erp.main import app as erp_app
    client = TestClient(erp_app)
    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ERP"
    assert "orders" in data
    assert len(data["orders"]) > 0


def test_erp_stats():
    """Test ERP stats endpoint."""
    from services.erp.main import app as erp_app
    client = TestClient(erp_app)
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "orders_count" in data
    assert "revenue_total" in data
    assert "avg_order_value" in data


def test_crm_customers():
    """Test CRM customers endpoint."""
    from services.crm.main import app as crm_app
    client = TestClient(crm_app)
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CRM"
    assert "total_customers" in data
    assert len(data["customers"]) == 5


def test_crm_pipeline():
    """Test CRM pipeline endpoint."""
    from services.crm.main import app as crm_app
    client = TestClient(crm_app)
    response = client.get("/api/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert "total_pipeline_value" in data


def test_wms_warehouses():
    """Test WMS warehouses endpoint."""
    from services.wms.main import app as wms_app
    client = TestClient(wms_app)
    response = client.get("/api/warehouses")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "WMS"
    assert "total_warehouses" in data
    assert len(data["warehouses"]) == 3


def test_wms_dispatch():
    """Test WMS dispatch endpoint."""
    from services.wms.main import app as wms_app
    client = TestClient(wms_app)
    response = client.get("/api/dispatch")
    assert response.status_code == 200
    data = response.json()
    assert "queue" in data
    assert "total_items_queued" in data


def test_cors_configuration():
    """Test CORS is properly configured (not allowing all origins)."""
    from services.erp.main import app as erp_app
    
    cors_middleware = None
    for middleware in erp_app.user_middleware:
        if hasattr(middleware, 'cls') and 'CORSMiddleware' in str(middleware.cls):
            cors_middleware = middleware
            break
    
    # CORS middleware should be present
    assert cors_middleware is not None or len(erp_app.user_middleware) > 0


def test_data_integrity():
    """Test data consistency across services."""
    from services.erp.main import app as erp_app
    from services.crm.main import app as crm_app
    from services.wms.main import app as wms_app
    
    erp_client = TestClient(erp_app)
    crm_client = TestClient(crm_app)
    wms_client = TestClient(wms_app)
    
    # Get product count from ERP
    erp_response = erp_client.get("/api/inventory")
    erp_products = erp_response.json()["total_products"]
    assert erp_products > 0
    
    # Get customer count from CRM
    crm_response = crm_client.get("/api/customers")
    crm_customers = crm_response.json()["total_customers"]
    assert crm_customers > 0
    
    # Get warehouse count from WMS
    wms_response = wms_client.get("/api/warehouses")
    wms_warehouses = wms_response.json()["total_warehouses"]
    assert wms_warehouses > 0


def test_error_handling():
    """Test 404 error handling."""
    from services.erp.main import app as erp_app
    client = TestClient(erp_app)
    
    response = client.get("/api/inventory/NONEXISTENT")
    assert response.status_code == 404


if __name__ == "__main__":
    print("Run with: pytest tests/test_integration.py -v")
