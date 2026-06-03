# GitHub Setup Guide

## Fork or Create the Repository

### Option 1: Fork from Template (Recommended)
1. Fork this repo to your GitHub account: https://github.com/cloud-erp-platform/cloud-erp-platform/fork
2. Clone your fork: `git clone https://github.com/YOUR-ORG/cloud-erp-platform.git`
3. Make it public (Settings → Visibility → Public)

### Option 2: Create New Repo
1. Create a new GitHub repo
2. Clone and add this code:
```bash
git clone https://github.com/cloud-erp-platform/cloud-erp-platform.git
cd cloud-erp-platform
git remote set-url origin https://github.com/YOUR-ORG/cloud-erp-platform.git
git push -u origin main
```

---

## Configure for AWS Deployment

### Step 1: Add Deployment Secrets (Optional, for CI/CD)

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Add these if you want automated deployments:
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
TF_VAR_admin_cidr=YOUR.IP.ADDR.ESS/32
```

### Step 2: Update Terraform Variables

Edit `terraform/terraform.tfvars` with your values:
```hcl
repo_url = "https://github.com/YOUR-ORG/cloud-erp-platform.git"
key_pair_name = "cloud-erp-key"
admin_cidr = "203.0.113.45/32"  # Your public IP
```

---

## Protect Main Branch (Recommended)

Settings → Branches → Add rule → Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
  - Require: "Cloud ERP Platform CI"
  - Require: "Terraform Validate"

---

## CI/CD Status

The following workflows run automatically:

### ✅ Cloud ERP Platform CI (on every push)
- Python 3.12 setup
- Validation tests
- Integration tests
- Docker build & service tests
- Performance testing with Locust

### ✅ Terraform Validate (on terraform/ changes)
- Format check
- Terraform init
- Terraform validate

---

## Local Development Workflow

```bash
# 1. Clone your fork
git clone https://github.com/YOUR-ORG/cloud-erp-platform.git
cd cloud-erp-platform

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes & test locally
docker compose up --build
pytest tests/test_integration.py -v
bash validate.sh

# 4. Commit & push
git add .
git commit -m "feat: description"
git push origin feature/my-feature

# 5. Create Pull Request on GitHub
# CI automatically runs all tests
# Merge when all checks pass

# 6. Deploy to AWS
# After merge to main, you can run:
bash deploy.sh
```

---

## GitHub Actions Secrets for Auto-Deploy (Advanced)

To enable one-click deployment from GitHub:

1. Create AWS IAM user with:
   - EC2 full access
   - VPC full access
   - IAM read-only

2. Create access key (save securely)

3. Add to GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

4. Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'
      - 'docker-compose.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: |
          cd terraform
          terraform init -backend=false
          terraform apply -auto-approve
```

---

## Domain Setup (Optional)

### CloudFlare (Recommended)
1. Add domain to CloudFlare
2. Point nameservers to CloudFlare
3. Create A record: `api.yourdomain.com` → `<gateway_public_ip>`
4. Enable SSL (automatic with CloudFlare)

### Manual Route53
```bash
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s)

# Add A record pointing to gateway IP
```

---

## Troubleshooting

**Q: GitHub Actions failing?**
A: Check workflow logs: Actions tab → latest run → view logs

**Q: Tests failing locally?**
A: Ensure Python 3.12+, install: `pip install -r tests/requirements.txt`

**Q: Docker build failing?**
A: Try: `docker compose build --no-cache`

---

## Next Steps

- [ ] Fork the repo
- [ ] Configure terraform.tfvars
- [ ] Run `bash deploy.sh`
- [ ] Test API endpoints
- [ ] Configure custom domain
- [ ] Set up monitoring (CloudWatch)
