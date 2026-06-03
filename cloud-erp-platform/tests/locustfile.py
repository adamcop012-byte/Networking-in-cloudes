"""
Performance & Scalability Tests — Locust
==========================================
Unit 6 — Learning Aim C (C.M3) and D (D.M4)

Covers:
  - All three services through the Nginx gateway
  - Measures requests/sec, response time, failure rate
  - Two user classes: LightUser (normal load) and HeavyUser (stress test)

Run:
  # Interactive UI at http://localhost:8089
  locust -f locustfile.py --host http://localhost

  # Headless (CI / evidence screenshot)
  locust -f locustfile.py --host http://localhost \
         --users 50 --spawn-rate 5 --run-time 60s --headless \
         --html report.html
"""

from locust import HttpUser, TaskSet, between, task


# ── ERP Task Set ──────────────────────────────────────────────────────────────
class ERPTasks(TaskSet):
    @task(3)
    def get_inventory(self):
        with self.client.get("/erp/api/inventory", name="ERP: GET /inventory", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Expected 200, got {r.status_code}")

    @task(2)
    def get_orders(self):
        with self.client.get("/erp/api/orders", name="ERP: GET /orders", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Expected 200, got {r.status_code}")

    @task(1)
    def get_erp_stats(self):
        self.client.get("/erp/api/stats", name="ERP: GET /stats")

    @task(1)
    def get_single_product(self):
        self.client.get("/erp/api/inventory/P001", name="ERP: GET /inventory/P001")

    @task(1)
    def erp_health(self):
        self.client.get("/erp/health", name="ERP: GET /health")


# ── CRM Task Set ──────────────────────────────────────────────────────────────
class CRMTasks(TaskSet):
    @task(3)
    def get_customers(self):
        with self.client.get("/crm/api/customers", name="CRM: GET /customers", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Expected 200, got {r.status_code}")

    @task(2)
    def get_pipeline(self):
        self.client.get("/crm/api/pipeline", name="CRM: GET /pipeline")

    @task(1)
    def get_activity(self):
        self.client.get("/crm/api/activity", name="CRM: GET /activity")

    @task(1)
    def crm_health(self):
        self.client.get("/crm/health", name="CRM: GET /health")


# ── WMS Task Set ──────────────────────────────────────────────────────────────
class WMSTasks(TaskSet):
    @task(3)
    def get_warehouses(self):
        with self.client.get("/wms/api/warehouses", name="WMS: GET /warehouses", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Expected 200, got {r.status_code}")

    @task(2)
    def get_stock_movements(self):
        self.client.get("/wms/api/stock-movements", name="WMS: GET /stock-movements")

    @task(1)
    def get_dispatch(self):
        self.client.get("/wms/api/dispatch", name="WMS: GET /dispatch")

    @task(1)
    def wms_health(self):
        self.client.get("/wms/health", name="WMS: GET /health")


# ── User Classes ──────────────────────────────────────────────────────────────

class LightUser(HttpUser):
    """
    Normal business load — simulates regular staff usage during the day.
    C.M3 baseline test: 10–20 users, measure average response time.
    """
    wait_time = between(1, 3)       # 1–3 seconds between requests

    tasks = {
        ERPTasks: 2,                # ERP gets most traffic (order processing)
        CRMTasks: 1,
        WMSTasks: 1,
    }


class HeavyUser(HttpUser):
    """
    Stress test — simulates peak load (e.g. end-of-season bulk orders).
    D.M4 enhancement test: 50–100 users, check response time holds under load.
    Expected result: p95 response time < 200ms through Nginx gateway.
    """
    wait_time = between(0.1, 0.5)   # rapid-fire requests

    tasks = {
        ERPTasks: 3,
        CRMTasks: 1,
        WMSTasks: 2,
    }
