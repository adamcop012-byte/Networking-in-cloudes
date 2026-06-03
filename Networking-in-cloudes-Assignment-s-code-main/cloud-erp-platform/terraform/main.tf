# =============================================================================
#  Terraform — AWS Cloud Infrastructure
#  Unit 6: Networking in the Cloud
#  ─────────────────────────────────────
#  Deploys the same architecture as docker-compose.yml but on real AWS:
#    VPC → 2 Subnets → Security Groups → EC2 instances → ALB
# =============================================================================

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── VPC ───────────────────────────────────────────────────────────────────────
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ── Internet Gateway (allows public subnet to reach internet) ─────────────────
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "${var.project_name}-igw" }
}

# ── Public Subnet (Nginx API Gateway lives here) ──────────────────────────────
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
    Tier = "public"
  }
}

# ── Private Subnet (ERP, CRM, WMS live here — no direct internet access) ─────
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${var.project_name}-private-subnet"
    Tier = "private"
  }
}

# ── Route Table: Public → Internet Gateway ────────────────────────────────────
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ── NAT Gateway (private subnet can initiate outbound, e.g. pip install) ─────
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = { Name = "${var.project_name}-nat-eip" }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
  tags          = { Name = "${var.project_name}-nat" }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = { Name = "${var.project_name}-private-rt" }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# ── Security Group: Public (API Gateway) ──────────────────────────────────────
# Allows HTTP/HTTPS from internet. SSH only from admin CIDR.
resource "aws_security_group" "public_sg" {
  name        = "${var.project_name}-public-sg"
  description = "Public subnet — API Gateway. Allow HTTP/HTTPS inbound."
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH from admin only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-public-sg" }
}

# ── Security Group: Private (ERP / CRM / WMS) ────────────────────────────────
# Only accepts traffic FROM the public security group (Nginx gateway).
# No direct internet access — this is the key security control.
resource "aws_security_group" "private_sg" {
  name        = "${var.project_name}-private-sg"
  description = "Private subnet — ERP/CRM/WMS. Only accept from gateway SG."
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ERP port from gateway only"
    from_port       = 8001
    to_port         = 8001
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }

  ingress {
    description     = "CRM port from gateway only"
    from_port       = 8002
    to_port         = 8002
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }

  ingress {
    description     = "WMS port from gateway only"
    from_port       = 8003
    to_port         = 8003
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-private-sg" }
}

# ── EC2: API Gateway (Nginx) in Public Subnet ────────────────────────────────
resource "aws_instance" "gateway" {
  ami                    = var.ami_id
  instance_type          = var.instance_type_gateway
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.public_sg.id]
  key_name               = var.key_pair_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    cd /home/ubuntu
    git clone ${var.repo_url} app
    cd app
    docker compose up -d gateway
  EOF

  tags = {
    Name    = "${var.project_name}-gateway"
    Role    = "api-gateway"
    Subnet  = "public"
  }
}

# ── EC2: ERP Service in Private Subnet ───────────────────────────────────────
resource "aws_instance" "erp" {
  ami                    = var.ami_id
  instance_type          = var.instance_type_service
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.private_sg.id]
  key_name               = var.key_pair_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl enable docker && systemctl start docker
    cd /home/ubuntu
    git clone ${var.repo_url} app
    cd app/services/erp
    docker build -t erp-service .
    docker run -d -p 8001:8001 --name erp erp-service
  EOF

  tags = { Name = "${var.project_name}-erp", Role = "erp", Subnet = "private" }
}

# ── EC2: CRM Service in Private Subnet ───────────────────────────────────────
resource "aws_instance" "crm" {
  ami                    = var.ami_id
  instance_type          = var.instance_type_service
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.private_sg.id]
  key_name               = var.key_pair_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl enable docker && systemctl start docker
    cd /home/ubuntu
    git clone ${var.repo_url} app
    cd app/services/crm
    docker build -t crm-service .
    docker run -d -p 8002:8002 --name crm crm-service
  EOF

  tags = { Name = "${var.project_name}-crm", Role = "crm", Subnet = "private" }
}

# ── EC2: WMS Service in Private Subnet ───────────────────────────────────────
resource "aws_instance" "wms" {
  ami                    = var.ami_id
  instance_type          = var.instance_type_service
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.private_sg.id]
  key_name               = var.key_pair_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl enable docker && systemctl start docker
    cd /home/ubuntu
    git clone ${var.repo_url} app
    cd app/services/wms
    docker build -t wms-service .
    docker run -d -p 8003:8003 --name wms wms-service
  EOF

  tags = { Name = "${var.project_name}-wms", Role = "wms", Subnet = "private" }
}
