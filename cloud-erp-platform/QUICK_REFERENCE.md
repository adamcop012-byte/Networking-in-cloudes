# 📋 Quick Reference — Cloud ERP Platform

## Files & What They Do

| File/Folder | Purpose | Who Uses |
|---|---|---|
| `README.md` | Main overview & quick start | Everyone first |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step deployment guide | Deployment person (start here!) |
| `CLOUD_DEPLOYMENT.md` | Detailed AWS architecture & troubleshooting | Cloud engineer |
| `GITHUB_SETUP.md` | GitHub repo configuration for CI/CD | DevOps/Git person |
| `.env.example` | Environment variables template | Local development |
| `terraform/` | AWS Infrastructure as Code | Deployment automation |
| `docker-compose.yml` | Local Docker simulation of VPC | Local testing |
| `deploy.sh` | One-command deployment script | Quick deployment |
| `services/` | ERP, CRM, WMS microservices | Developers |
| `tests/` | Integration & performance tests | QA/Testing |
| `gateway/` | Nginx reverse proxy config | Network engineers |
| `dashboard/` | Web UI (HTML/CSS/JS) | Frontend developers |

---

## Getting Started (Choose One)

### 🏠 Local Testing (5 minutes)
For testing the architecture on your machine:
```bash
docker compose up --build
open http://localhost
```
**See**: [README.md](README.md) → "Quick Start"

### ☁️ AWS Cloud Deployment (30 minutes)
For deploying to production on AWS:
```bash
bash deploy.sh
# Follow prompts...
```
**See**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) ← Start here!

---

## Architecture at a Glance

```
┌─ AWS VPC 10.0.0.0/16 ─────────────────────────┐
│                                                 │
│ PUBLIC: 10.0.1.0/24        PRIVATE: 10.0.2.0/24
│ ┌─────────────────┐        ┌────────────────────┐
│ │ Nginx Gateway   │        │ ERP Service        │
│ │ (t3.micro)      │───────→│ (t3.small)         │
│ │ :80 HTTPS       │        │ :8001 private only │
│ └─────────────────┘        └────────────────────┘
│                            ┌────────────────────┐
│  Internet-facing           │ CRM Service        │
│  (anyone can access)       │ (t3.small)         │
│                            │ :8002 private only │
│                            └────────────────────┘
│                            ┌────────────────────┐
│                            │ WMS Service        │
│                            │ (t3.small)         │
│                            │ :8003 private only │
│                            └────────────────────┘
│                                                 │
│  Key: Private services can NOT be reached      │
│       from internet. Only via Nginx gateway.  │
└─────────────────────────────────────────────────┘
```

---

## Services Overview

| Service | Port | Purpose | Data |
|---------|------|---------|------|
| **Gateway** | 80 | Nginx reverse proxy | Routes traffic |
| **ERP** | 8001 | Orders & Inventory | 10 products, 7 orders |
| **CRM** | 8002 | Customers & Pipeline | 5 customers, 4 deals |
| **WMS** | 8003 | Warehouses & Dispatch | 3 warehouses, dispatch queue |

---

## Key Concepts Demonstrated

✅ **VPC Networking**: Isolated network with subnets  
✅ **Public/Private Subnets**: Gateway exposed, services hidden  
✅ **Security Groups**: Firewall rules between tiers  
✅ **NAT Gateway**: Private subnet outbound access  
✅ **API Gateway**: Reverse proxy, rate limiting  
✅ **Microservices**: Independent services, isolated scalability  
✅ **Docker**: Containerized deployment  
✅ **IaC (Terraform)**: Infrastructure as Code for reproducibility  

---

## Important Files to Customize

Before deploying, you MUST update:

1. **`terraform/terraform.tfvars`** (copy from `.example`)
   - Your GitHub repo URL
   - Your SSH key pair name  
   - Your public IP (for SSH access)

2. **.env** (copy from `.example`)
   - CORS origins for your domain

3. Optional: **Gateway domain** (`.github/workflows/deploy.yml`)
   - For automated deployments

---

## Deployment Timeline

| Phase | Time | What Happens |
|-------|------|--------------|
| Setup & Prerequisites | 10 min | Install tools, create AWS account, SSH keys |
| Configuration | 5 min | Edit terraform.tfvars |
| Plan & Review | 5 min | Terraform plan to review resources |
| Deploy | 3 min | Terraform apply creates resources |
| Services Boot | 5-10 min | EC2 downloads Docker, builds images, starts services |
| Testing | 5 min | Verify endpoints work |
| **Total** | **30-40 min** | **Live platform on AWS** ✅ |

---

## Costs

**Estimated Monthly Cost**: $100-150

- t3.micro (gateway): ~$8
- 3× t3.small (services): ~$60
- NAT Gateway: ~$32
- EBS storage: ~$5
- Data transfer: ~$5-20

**To save money**:
- Use `t3.nano` for testing (~$4/month)
- Destroy when not in use (`terraform destroy`)
- Monitor with AWS billing alerts
- Use S3 for backups (cheaper than EBS)

---

## Quick Commands

```bash
# Local testing
docker compose up --build
pytest tests/test_integration.py -v

# AWS deployment
cd terraform
terraform init
terraform plan
terraform apply
terraform output gateway_public_ip  # Get your IP

# Testing
curl http://<gateway-ip>/health
curl http://<gateway-ip>/erp/api/orders

# Cleanup
terraform destroy
```

---

## Troubleshooting

**Services won't start?**
→ Wait 10 minutes, SSH in and check `docker logs`

**Can't SSH to EC2?**
→ Verify security group has SSH from your IP (check `admin_cidr` in `terraform.tfvars`)

**CORS errors in dashboard?**
→ Update `CORS_ORIGINS` in docker-compose.yml or EC2 environment variables

**High AWS costs?**
→ Destroy infrastructure immediately: `terraform destroy`

---

## Next Steps After Deployment

1. ✅ **Monitor**: Set up CloudWatch dashboards
2. ✅ **SSL/TLS**: Add HTTPS certificate to Nginx
3. ✅ **Backup**: Enable EBS snapshots
4. ✅ **Auto-scaling**: Configure EC2 Auto Scaling Groups
5. ✅ **Database**: Add RDS (PostgreSQL/MySQL)
6. ✅ **CI/CD**: Enable GitHub Actions auto-deploy

---

## Documentation Map

```
README.md                      ← Start here (overview)
  ├→ DEPLOYMENT_CHECKLIST.md   ← Then here (step-by-step)
  ├→ CLOUD_DEPLOYMENT.md       ← Detailed reference
  ├→ GITHUB_SETUP.md           ← For CI/CD
  └→ terraform/                ← AWS infrastructure
```

---

## Need Help?

1. **Beginner?** → Start with [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. **Questions about AWS?** → Check [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
3. **Docker/local issues?** → See [README.md](README.md) → Troubleshooting
4. **GitHub Actions?** → See [GITHUB_SETUP.md](GITHUB_SETUP.md)

---

**Ready to deploy?** 🚀  
→ Next: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
