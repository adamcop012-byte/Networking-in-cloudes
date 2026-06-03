#!/bin/bash
# =============================================================================
# Cloud ERP Platform — Quick Deploy Script
# =============================================================================
# This script automates the AWS deployment using Terraform

set -e  # Exit on error

echo "🚀 Cloud ERP Platform — AWS Deployment Script"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found. Install from: https://www.terraform.io/downloads${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Terraform installed${NC}"
echo -e "${GREEN}✓ AWS CLI installed${NC}"

# Verify AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run: aws configure${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
echo -e "${GREEN}✓ AWS Account: $ACCOUNT_ID (Region: $REGION)${NC}"
echo ""

# Check for terraform.tfvars
cd terraform

if [ ! -f terraform.tfvars ]; then
    echo -e "${YELLOW}⚠️  terraform.tfvars not found${NC}"
    echo "Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo -e "${YELLOW}⚠️  Edit terraform/terraform.tfvars with your values!${NC}"
    echo ""
    echo "Key values to update:"
    echo "  - repo_url: Your GitHub repo"
    echo "  - key_pair_name: Your EC2 key pair"
    echo "  - admin_cidr: Your public IP"
    echo ""
    read -p "Press Enter after updating terraform.tfvars..."
fi

# Validate Terraform
echo "🔍 Validating Terraform configuration..."
terraform init
terraform validate
terraform fmt -recursive

echo -e "${GREEN}✓ Terraform configuration valid${NC}"
echo ""

# Show plan
echo "📊 Terraform Plan (review before confirming)..."
terraform plan -out=tfplan

echo ""
echo -e "${YELLOW}⚠️  Review the plan above. This will create:${NC}"
echo "   - 1 VPC with 2 subnets"
echo "   - 4 EC2 instances (1 gateway + 3 services)"
echo "   - NAT Gateway, Internet Gateway, Security Groups"
echo "   - Estimated cost: ~$30-50/month (t3.micro + t3.small)"
echo ""

read -p "Continue with deployment? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Deploy
echo "🚀 Deploying infrastructure to AWS..."
terraform apply tfplan

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Show outputs
echo "📍 Deployment Outputs:"
GATEWAY_IP=$(terraform output -raw gateway_public_ip 2>/dev/null || echo "pending")
VPC_ID=$(terraform output -raw vpc_id 2>/dev/null || echo "pending")
PUBLIC_SUBNET=$(terraform output -raw public_subnet_id 2>/dev/null || echo "pending")
PRIVATE_SUBNET=$(terraform output -raw private_subnet_id 2>/dev/null || echo "pending")

echo "   Gateway Public IP: $GATEWAY_IP"
echo "   VPC ID: $VPC_ID"
echo "   Public Subnet: $PUBLIC_SUBNET"
echo "   Private Subnet: $PRIVATE_SUBNET"
echo ""

echo -e "${YELLOW}⏳ Services are starting (5-10 minutes)...${NC}"
echo ""

if [ "$GATEWAY_IP" != "pending" ] && [ "$GATEWAY_IP" != "" ]; then
    echo "Quick test commands:"
    echo ""
    echo "  # SSH into gateway"
    echo "  ssh -i ~/.ssh/$(grep key_pair_name terraform.tfvars | cut -d'"' -f2).pem ubuntu@$GATEWAY_IP"
    echo ""
    echo "  # Test endpoints"
    echo "  curl http://$GATEWAY_IP/health"
    echo "  curl http://$GATEWAY_IP/erp/api/orders"
    echo "  curl http://$GATEWAY_IP/crm/api/customers"
    echo "  curl http://$GATEWAY_IP/wms/api/warehouses"
    echo ""
    echo "  # Open dashboard"
    echo "  open http://$GATEWAY_IP"
    echo ""
fi

echo "📚 Next steps:"
echo "   1. Wait 5-10 minutes for services to boot"
echo "   2. Test endpoints (see commands above)"
echo "   3. Configure your domain (see CLOUD_DEPLOYMENT.md)"
echo "   4. Monitor in CloudWatch console"
echo ""

echo "🧹 To destroy infrastructure (and stop costs):"
echo "   terraform destroy"
echo ""

echo -e "${GREEN}✨ Deployment script complete!${NC}"
