# Cloud ERP Platform ☁️

**Unit 6: Networking in the Cloud** — Pearson BTEC Higher Nationals in Digital Technologies

Wholesale clothing company cloud platform integrating ERP, CRM, and WMS in a VPC with public/private subnet isolation.

## 🚀 Quick Start

### Option 1: Local Testing (Docker Compose)

```bash
# Clone repo
git clone https://github.com/YOUR-ORG/cloud-erp-platform.git
cd cloud-erp-platform

# Run tests first
pytest tests/test_integration.py -v
bash validate.sh

# Start all services
docker compose up --build

# Open http://localhost
```

### Option 2: AWS Cloud Deployment (Production)

**👉 [See full AWS deployment guide »](CLOUD_DEPLOYMENT.md)**

Quick version:
```bash
# 1. Install prerequisites: Terraform, AWS CLI
# 2. Configure AWS credentials: aws configure
# 3. Create EC2 key pair: aws ec2 create-key-pair --key-name cloud-erp-key ...
# 4. Prepare Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 5. Deploy (creates VPC, subnets, security groups, 4× EC2 instances)
bash ../deploy.sh
# OR manually: terraform init && terraform plan && terraform apply

# 6. Wait 5-10 minutes for services to boot
# 7. Test with: curl http://<gateway_public_ip>/health
```

---

## Architecture

```
Internet
    │  (HTTP :80)
    ▼
┌──────────────────────────────────────────────┐
│  PUBLIC SUBNET  10.0.1.0/24                  │
│  ┌──────────────────────────────────────┐    │
│  │  Nginx API Gateway  (Security Group) │    │
│  │  Allows: HTTP/HTTPS from anywhere    │    │
│  └──────────┬───────────────────────────┘    │
└─────────────│────────────────────────────────┘
              │  (internal routing only)
┌─────────────│────────────────────────────────┐
│  PRIVATE SUBNET  10.0.2.0/24                 │
│             │                                │
│   ┌─────────┴──────────────────────────┐     │
│   │  Security Group:                   │     │
│   │  Allows ports 8001–8003            │     │
│   │  FROM gateway SG only              │     │
│   └──────────────────────────────────--┘     │
│                                              │
│   [ERP :8001]  [CRM :8002]  [WMS :8003]     │
│   Orders       Customers    Warehouse        │
│   Inventory    Pipeline     Dispatch         │
└──────────────────────────────────────────────┘
```

**Key networking concepts demonstrated:**
- **VPC** — isolated virtual network (`10.0.0.0/16`)
- **Public Subnet** — internet-facing, hosts the API Gateway only
- **Private Subnet** — no direct internet access (`internal: true` in Docker)
- **Security Groups** — port-level firewall rules between subnets
- **NAT Gateway** — private subnet can reach internet outbound (OS updates, pip)
- **API Gateway** — single entry point, routes traffic to private services

---

## Quick Start

### Local Development

```bash
git clone https://github.com/your-username/cloud-erp-platform.git
cd cloud-erp-platform

# Start all services
docker compose up --build

# Open http://localhost
```

**Services Started:**
| Container | Role | Network | Port |
|---|---|---|---|
| `gateway` | Nginx API Gateway | public + private | `:80` only |
| `erp` | ERP Service | private only | internal |
| `crm` | CRM Service | private only | internal |
| `wms` | WMS Service | private only | internal |

The ERP/CRM/WMS containers are not directly reachable—only through the gateway, exactly like a real VPC.

---

## Configuration

Copy `.env.example` to `.env` for your deployment:

```bash
cp .env.example .env

# For local testing:
CORS_ORIGINS=http://localhost,http://localhost:80

# For domain deployment:
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

---

## Testing

### Unit & Integration Tests

```bash
# Install dependencies
pip install -r tests/requirements.txt

# Run tests
pytest tests/test_integration.py -v

# Expected: 16 tests pass
#   ✓ All services import correctly
#   ✓ Health checks respond with 200
#   ✓ All data endpoints return valid data
#   ✓ CORS is restricted (not allow_origins=["*"])
#   ✓ Data integrity across services
#   ✓ Error handling (404 responses)
```

### Code Quality Validation

```bash
# Run configuration validation
bash validate.sh

# Expected output: All 10 checks pass
#   ✓ Version attribute removed from docker-compose.yml
#   ✓ CORS restricted with environment variables
#   ✓ requirements.txt in all services
#   ✓ Production Dockerfile settings
#   ✓ Environment variables configured
#   ✓ .env.example present
#   ✓ All API routes configured
#   ✓ Logging enabled
```

### Performance Testing (C.M3 / D.M4)

```bash
pip install locust

# Interactive UI (http://localhost:8089)
locust -f tests/locustfile.py --host http://localhost

# Headless report generation
locust -f tests/locustfile.py --host http://localhost \
       --users 50 --spawn-rate 5 --run-time 60s \
       --headless --html locust_report.html
```

**Test Profiles:**
- **LightUser** — normal load (1–3s delays between requests)
- **HeavyUser** — stress test (0.1–0.5s delays, peak season simulation)

Expected result: p95 response time < 200ms through Nginx gateway

---

## API Endpoints

| Path | Service | Description |
|---|---|---|
| `GET /` | Dashboard | Operations dashboard |
| `GET /health` | Gateway | Gateway health check |
| `GET /erp/health` | ERP | ERP service health |
| `GET /erp/api/inventory` | ERP | Product inventory (10 products) |
| `GET /erp/api/orders` | ERP | All orders (7 orders) |
| `GET /erp/api/stats` | ERP | Revenue & stock statistics |
| `GET /crm/health` | CRM | CRM service health |
| `GET /crm/api/customers` | CRM | Customer list (5 customers) |
| `GET /crm/api/pipeline` | CRM | Sales pipeline (4 deals) |
| `GET /wms/health` | WMS | WMS service health |
| `GET /wms/api/warehouses` | WMS | Warehouse utilization (3 warehouses) |
| `GET /wms/api/dispatch` | WMS | Dispatch queue |

---

## Production Deployment

**👉 [See detailed AWS Deployment Guide »](CLOUD_DEPLOYMENT.md)**

### Checklist
✅ **Code Quality**
- CORS properly restricted (environment variable, not `["*"]`)
- No hardcoded credentials in source code
- All dependencies pinned in requirements.txt
- Type hints in FastAPI endpoints

✅ **Infrastructure**
- Nginx rate limiting enabled (100 req/s)
- Services running with multiple workers (--workers 2)
- Health checks on all containers
- Restart policy: unless-stopped

✅ **Networking**
- Public subnet (10.0.1.0/24) — gateway only, internet-facing
- Private subnet (10.0.2.0/24) — ERP/CRM/WMS isolated
- Security groups restrict traffic (private only accepts from gateway SG)
- NAT Gateway for outbound access (pip install, OS updates)

### Quick Deploy
```bash
# One-command deployment
bash deploy.sh

# Manual deployment
cd terraform
cp terraform.tfvars.example terraform.tfvars  # Edit with your values
terraform init
terraform plan
terraform apply
```

### Verification
```bash
# After ~5-10 minutes, test your endpoints
GATEWAY_IP=$(terraform output -raw gateway_public_ip)
curl http://$GATEWAY_IP/health
curl http://$GATEWAY_IP/erp/api/orders
curl http://$GATEWAY_IP/crm/api/customers
curl http://$GATEWAY_IP/wms/api/warehouses
```

---

## Architecture Decisions

| Decision | Why |
|---|---|
| Docker Compose for local | Easy VPC simulation, no need for cloud account |
| Terraform for AWS | Infrastructure as Code, reproducible deployments |
| Nginx rate limiting | DDoS protection at gateway layer |
| Private subnets for services | Reduced attack surface, security best practice |
| CORS environment variable | Easy configuration for different domains |
| Multiple Uvicorn workers | Better concurrency, production readiness |

---

## Learning Outcomes

**Unit 6: Networking in the Cloud**

- **A.M1**: TCP/IP, HTTP/1.1, DNS, CIDR notation, TLS/SSL
- **A.P1**: Cloud models (IaaS/PaaS/SaaS), deployment models (private/public)
- **C.M3**: Performance testing with Locust (baseline load test)
- **D.M4**: Scalability testing (peak load stress test)

---

## Files Structure

```
cloud-erp-platform/
├── docker-compose.yml           # 2-subnet VPC simulation
├── gateway/
│   └── nginx.conf               # API gateway, rate limiting
├── services/
│   ├── erp/
│   │   ├── main.py              # ERP microservice
│   │   ├── Dockerfile           # Production-ready image
│   │   └── requirements.txt      # Dependencies
│   ├── crm/                      # CRM microservice
│   └── wms/                      # WMS microservice
├── dashboard/
│   ├── index.html               # Operations dashboard
│   ├── store.html               # Product store
│   └── checkout.html            # Order checkout
├── tests/
│   ├── locustfile.py            # Performance tests
│   └── test_integration.py      # Unit/integration tests
├── terraform/                   # AWS deployment
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .env.example                 # Configuration template
└── validate.sh                  # Code quality validation
```

---

## Troubleshooting

**Q: Docker compose fails to start services**
A: Ensure port 80 is not in use. Run `sudo lsof -i :80` to check.

**Q: Services fail health check**
A: Check logs with `docker compose logs erp`. Verify network connectivity between containers.

**Q: CORS errors in dashboard**
A: Ensure `CORS_ORIGINS` in docker-compose.yml matches your domain/localhost.

**Q: Tests fail to import services**
A: Install dependencies: `pip install fastapi uvicorn pytest httpx`

---

## License

BTEC Assignment — Educational Use Only

