# ✅ Deployment Checklist — Ready for Cloud

Everything has been prepared for immediate deployment to AWS. Follow this checklist in order:

---

## Phase 1: Prerequisites (10 mins)

### AWS Account Setup
- [ ] Create AWS account (https://aws.amazon.com)
- [ ] Create IAM user with EC2/VPC/ECS permissions
- [ ] Generate Access Key ID and Secret Access Key
- [ ] Save credentials in `~/.aws/credentials`:
  ```ini
  [default]
  aws_access_key_id = AKIA...
  aws_secret_access_key = ...
  ```

### Install Tools
- [ ] Install Terraform: `brew install terraform` (macOS) or see https://www.terraform.io/downloads
- [ ] Install AWS CLI: `brew install awscli` (macOS) or see https://aws.amazon.com/cli/
- [ ] Verify: `terraform version` and `aws --version`

### EC2 Key Pair
- [ ] Create SSH key pair in AWS (one-time):
  ```bash
  aws ec2 create-key-pair \
    --key-name cloud-erp-key \
    --region eu-west-1 \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/cloud-erp-key.pem
  chmod 600 ~/.ssh/cloud-erp-key.pem
  ```
- [ ] Verify key exists: `ls -la ~/.ssh/cloud-erp-key.pem`

### GitHub Repository
- [ ] Fork this repo: https://github.com/cloud-erp-platform/cloud-erp-platform/fork
- [ ] Clone your fork:
  ```bash
  git clone https://github.com/YOUR-ORG/cloud-erp-platform.git
  cd cloud-erp-platform
  ```
- [ ] Ensure repo is **public** (Settings → Visibility)
- [ ] Note your repo URL: `https://github.com/YOUR-ORG/cloud-erp-platform.git`

---

## Phase 2: Configuration (5 mins)

### Configure Terraform Variables
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
- [ ] `repo_url` = your GitHub repo URL
- [ ] `key_pair_name` = "cloud-erp-key" (or your key pair name)
- [ ] `admin_cidr` = "YOUR.IP.ADDRESS/32" (find with: `curl https://ifconfig.me`)
- [ ] `aws_region` = "eu-west-1" (or your preferred region)

### Verify Configuration
```bash
terraform init
terraform validate
terraform fmt -recursive
```

Expected: ✅ Success! The configuration is valid.

---

## Phase 3: Plan & Review (5 mins)

### Review Infrastructure Plan
```bash
terraform plan -out=tfplan
```

Expected resources:
- [ ] 1 VPC (10.0.0.0/16)
- [ ] 2 Subnets (public 10.0.1.0/24, private 10.0.2.0/24)
- [ ] 2 Security Groups (public + private)
- [ ] 4 EC2 instances (1 gateway, 3 services)
- [ ] 1 Internet Gateway
- [ ] 1 NAT Gateway + 1 Elastic IP
- [ ] 2 Route Tables

**Review the plan carefully.** Confirm all resources look correct.

---

## Phase 4: Deploy to AWS (2-3 mins)

### Apply Terraform
```bash
terraform apply tfplan
```

When prompted: Type `yes` to confirm

Expected output:
```
Apply complete! Resources: 26 added, 0 changed, 0 destroyed.

Outputs:
gateway_public_ip = "54.123.45.67"
```

**Save this IP** — it's your API Gateway endpoint!

### What's Happening
- Terraform is creating VPC, subnets, security groups
- Launching 4 EC2 instances with Docker
- Each instance running a `user_data` script to clone your repo and start services
- NAT Gateway being configured for outbound internet access

---

## Phase 5: Wait for Services (5-10 mins)

Services are booting and downloading dependencies. **Do NOT skip this step.**

### Monitor Boot Progress
```bash
# Check service statuses
cd terraform
GATEWAY_IP=$(terraform output -raw gateway_public_ip)

# Option 1: SSH into gateway and check Docker
ssh -i ~/.ssh/cloud-erp-key.pem ubuntu@$GATEWAY_IP
docker ps -a
docker logs api-gateway

# Option 2: Watch Terraform state
watch terraform show
```

Expected progress:
1. EC2 instances starting (2-3 mins)
2. Docker installation & configuration (1-2 mins)
3. Git clone from your repo (1 min)
4. Docker images building (2-3 mins)
5. Containers starting (1 min)
6. Health checks passing (1-2 mins)

**When all services are healthy: Ready for testing!**

---

## Phase 6: Test Deployment (5 mins)

### Get Your Gateway IP
```bash
cd terraform
GATEWAY_IP=$(terraform output -raw gateway_public_ip)
echo $GATEWAY_IP  # e.g., 54.123.45.67
```

### Test API Endpoints
```bash
# Health check (gateway)
curl http://$GATEWAY_IP/health

# ERP Service
curl http://$GATEWAY_IP/erp/health
curl http://$GATEWAY_IP/erp/api/orders
curl http://$GATEWAY_IP/erp/api/inventory

# CRM Service
curl http://$GATEWAY_IP/crm/health
curl http://$GATEWAY_IP/crm/api/customers
curl http://$GATEWAY_IP/crm/api/pipeline

# WMS Service
curl http://$GATEWAY_IP/wms/health
curl http://$GATEWAY_IP/wms/api/warehouses
curl http://$GATEWAY_IP/wms/api/dispatch

# Dashboard
open http://$GATEWAY_IP
```

Expected results:
- ✅ All health checks return `{"status": "healthy"}`
- ✅ Data endpoints return JSON with data
- ✅ Dashboard loads in browser
- ✅ No CORS errors in browser console

### Performance Test (Optional)
```bash
cd ..
pip install locust
locust -f tests/locustfile.py \
  --host http://$GATEWAY_IP \
  --users 10 --spawn-rate 2 --run-time 30s \
  --headless --only-summary
```

Expected: p95 response time < 200ms

---

## Phase 7: Setup Custom Domain (Optional)

If you want a nice domain instead of an IP:

### Option A: CloudFlare (Easiest)
1. Move domain to CloudFlare (free)
2. Create A record: `api.yourdomain.com` → `$GATEWAY_IP`
3. Wait 5 minutes for DNS propagation
4. Test: `curl https://api.yourdomain.com/health`

### Option B: Route53
```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s)

# Create A record (replace ZONE_ID)
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$GATEWAY_IP'"}]
      }
    }]
  }'
```

---

## Phase 8: Monitor & Maintain

### View Logs
```bash
# SSH into gateway
ssh -i ~/.ssh/cloud-erp-key.pem ubuntu@$GATEWAY_IP

# View Docker logs
docker logs -f api-gateway
docker logs -f erp-service
docker logs -f crm-service
docker logs -f wms-service
```

### Update Services
```bash
# SSH into gateway
ssh -i ~/.ssh/cloud-erp-key.pem ubuntu@$GATEWAY_IP

# Pull latest code
cd app
git pull origin main

# Rebuild and restart
docker compose up -d --build
```

### Monitor Costs
- **t3.micro gateway**: ~$7/month
- **3× t3.small services**: ~$60/month
- **NAT Gateway**: ~$32/month
- **EBS storage**: ~$5/month
- **Total: ~$100/month**

To minimize costs:
- Use `t3.nano` or `t4g.micro` for non-production
- Destroy when not in use: `terraform destroy`
- Enable AWS billing alerts

---

## Cleanup: Destroy Infrastructure

When you're done or want to stop costs:

```bash
cd terraform
terraform destroy

# When prompted: type 'yes' to confirm
# All AWS resources will be deleted (VPC, EC2, NAT, etc.)
```

This is **non-reversible** — use only when done testing!

---

## Troubleshooting

### ❌ "terraform: command not found"
→ Install Terraform: https://www.terraform.io/downloads

### ❌ "error: NoCredentialProviders"
→ Configure AWS: `aws configure` (enter your access keys)

### ❌ "error: EC2 key pair 'cloud-erp-key' does not exist"
→ Create key pair: `aws ec2 create-key-pair --key-name cloud-erp-key ...`

### ❌ "curl: (7) Failed to connect"
→ Gateway still booting. Wait 5-10 minutes and try again.

### ❌ "curl: (52) Empty reply from server"
→ Docker container crashed. SSH in and check: `docker logs api-gateway`

### ❌ Services slow or timing out
→ Upgrade to larger instances in `terraform.tfvars`:
- `instance_type_gateway = "t3.small"`
- `instance_type_service = "t3.medium"`

### ❌ DNS not resolving domain
→ Ensure nameservers are updated (CloudFlare/Route53)
→ Wait 30-60 minutes for global propagation

---

## Success! 🎉

Your cloud ERP platform is now live on AWS!

**Next steps:**
- [ ] Set up monitoring (CloudWatch)
- [ ] Enable automatic backups
- [ ] Configure SSL/TLS on Nginx
- [ ] Set up CI/CD pipeline
- [ ] Plan for auto-scaling

Questions? Check [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for detailed docs.

Happy deploying! 🚀
