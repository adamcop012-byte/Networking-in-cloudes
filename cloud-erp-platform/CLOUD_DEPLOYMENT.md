# 🚀 Cloud ERP Platform — AWS Deployment Guide

## Prerequisites

### 1. AWS Account & CLI
```bash
# Install AWS CLI v2
# macOS: brew install awscliv2
# Linux: apt-get install awscli
# Windows: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure
# Enter:
#   AWS Access Key ID: [from IAM console]
#   AWS Secret Access Key: [from IAM console]
#   Default region: eu-west-1
#   Default output: json

# Verify connection
aws ec2 describe-regions
```

### 2. Terraform
```bash
# Install Terraform >= 1.5
# macOS: brew install terraform
# Linux: https://www.terraform.io/downloads

terraform version
```

### 3. GitHub Repository (Fork or Create)
- Fork this repo to your GitHub account
- Ensure your repo is **public** (for EC2 to clone without auth)
- Note your repo URL: `https://github.com/YOUR-ORG/cloud-erp-platform.git`

### 4. EC2 Key Pair
Create a key pair for SSH access (this is required for Terraform):
```bash
aws ec2 create-key-pair \
  --key-name cloud-erp-key \
  --region eu-west-1 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/cloud-erp-key.pem

chmod 600 ~/.ssh/cloud-erp-key.pem
```

---

## Step 1: Prepare Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your details:
```hcl
# Your GitHub repo (EC2 will clone from here)
repo_url = "https://github.com/YOUR-ORG/cloud-erp-platform.git"

# Your SSH key pair name
key_pair_name = "cloud-erp-key"

# Your public IP (for SSH access)
# Find your IP: curl https://ifconfig.me
admin_cidr = "203.0.113.45/32"  # Replace with YOUR IP/32

# Your AWS region
aws_region = "eu-west-1"
```

---

## Step 2: Validate Terraform

```bash
terraform init
terraform validate
terraform fmt -recursive
```

Expected output:
```
Success! The configuration is valid.
```

---

## Step 3: Plan & Review Infrastructure

```bash
terraform plan -out=tfplan
```

This shows all resources that will be created:
- VPC (10.0.0.0/16)
- 2 Subnets (public 10.0.1.0/24, private 10.0.2.0/24)
- Security Groups (gateway + services)
- 4 EC2 instances (1 gateway, 3 services)
- NAT Gateway + EIP for outbound access
- Internet Gateway

Review and confirm everything looks correct.

---

## Step 4: Deploy to AWS

```bash
# Apply the terraform plan
terraform apply tfplan

# When complete, Terraform outputs the gateway's public IP
# Example output:
#   gateway_public_ip = "54.123.45.67"
```

**Save this IP** — it's your API Gateway endpoint.

---

## Step 5: Wait for Services to Boot

EC2 instances run a `user_data` script on startup that:
1. Installs Docker & Docker Compose
2. Clones your repository
3. Builds & starts the services

**Allow 5-10 minutes** for all services to become healthy.

Monitor progress:
```bash
# SSH into the gateway to check logs
ssh -i ~/.ssh/cloud-erp-key.pem ubuntu@<gateway_public_ip>

# View Docker containers
docker ps -a
docker logs api-gateway
docker logs erp-service
```

---

## Step 6: Test Your Deployment

```bash
# Replace with your gateway public IP
GATEWAY_IP="54.123.45.67"

# Test API Gateway
curl http://$GATEWAY_IP/health

# Test ERP service (via gateway)
curl http://$GATEWAY_IP/erp/health
curl http://$GATEWAY_IP/erp/api/orders

# Test CRM service
curl http://$GATEWAY_IP/crm/health
curl http://$GATEWAY_IP/crm/api/customers

# Test WMS service
curl http://$GATEWAY_IP/wms/health
curl http://$GATEWAY_IP/wms/api/warehouses

# View the dashboard
open http://$GATEWAY_IP
```

---

## Step 7: Configure Your Domain (Optional)

To use a custom domain instead of IP:

```bash
# 1. Create a Route53 hosted zone for your domain
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# 2. Point your domain registrar to Route53 nameservers

# 3. Create an A record pointing to the gateway IP
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "54.123.45.67"}]
      }
    }]
  }'

# 4. Update CORS origins in the ERP/CRM/WMS services
#    Edit services/*/main.py to allow https://yourdomain.com
```

---

## Security Checklist

- ✅ Private subnet services (ERP/CRM/WMS) are NOT exposed to the internet
- ✅ Only the Nginx gateway is internet-facing
- ✅ Gateway has restricted SSH access (admin_cidr only)
- ✅ Services communicate via private security group rules
- ✅ NAT Gateway allows outbound for OS updates & pip install

**Before production:**
- [ ] Restrict `admin_cidr` to your actual IP(s)
- [ ] Update CORS_ORIGINS to your domain
- [ ] Enable HTTPS/TLS on the gateway (add SSL cert to nginx.conf)
- [ ] Set up CloudWatch monitoring & alarms
- [ ] Configure backup & disaster recovery

---

## Cleanup (Destroy Infrastructure)

```bash
cd terraform
terraform destroy

# Confirm when prompted
```

---

## Troubleshooting

### Services are stuck "not running"
```bash
# SSH into each instance and check Docker logs
ssh -i ~/.ssh/cloud-erp-key.pem ubuntu@<private-ip>
docker logs <service-name>
```

### Gateway can't reach private services
- Verify security group rules (private subnet only allows traffic from public SG)
- Check nginx.conf upstream declarations

### High costs?
- Use smaller instances: `t3.nano` or `t4g.micro`
- Destroy unused infrastructure immediately (don't leave running)

---

## Architecture Diagram

```
┌─────────────────── AWS VPC 10.0.0.0/16 ──────────────────┐
│                                                             │
│ PUBLIC SUBNET 10.0.1.0/24  ─┐                             │
│ (Internet-Facing)           │                             │
│                             │ NAT Gateway                 │
│ ┌─────────────────────┐    │ (for outbound)              │
│ │ Nginx API Gateway   │────┼─→ Internet                  │
│ │ t3.micro            │    │                             │
│ │ Security Group:     │    │                             │
│ │ - HTTP :80          │    │                             │
│ │ - HTTPS :443        │    │                             │
│ │ - SSH :22 (admin)   │    │                             │
│ └──────────┬──────────┘    │                             │
│            │               │                             │
│            └───────────────┼─────────────────────┐       │
│                            │                     │       │
│ PRIVATE SUBNET 10.0.2.0/24 │                     │       │
│ (Isolated, no internet)    │                     │       │
│                            ▼                     ▼       │
│  ┌──────────────────┐ ┌──────────────────┐              │
│  │ ERP Service      │ │ CRM Service      │              │
│  │ t3.small         │ │ t3.small         │              │
│  │ Port 8001        │ │ Port 8002        │              │
│  │ Private only     │ │ Private only     │              │
│  └──────────────────┘ └──────────────────┘              │
│                                                          │
│  ┌──────────────────┐                                   │
│  │ WMS Service      │                                   │
│  │ t3.small         │                                   │
│  │ Port 8003        │                                   │
│  │ Private only     │                                   │
│  └──────────────────┘                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## What's Next?

1. **Monitoring**: Set up CloudWatch dashboards & alarms
2. **CI/CD**: Enable GitHub Actions for automatic tests & deployment
3. **SSL/TLS**: Add SSL certificate to Nginx
4. **Auto-scaling**: Configure EC2 Auto Scaling Groups
5. **Database**: Add RDS (PostgreSQL) for persistent data
6. **Backup**: Set up AWS Backup for EBS snapshots
