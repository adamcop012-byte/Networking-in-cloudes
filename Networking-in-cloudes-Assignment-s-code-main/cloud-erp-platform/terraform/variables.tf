variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Used as prefix for all resource names"
  type        = string
  default     = "hotelos-cloud"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI (region-specific — update for your region)"
  type        = string
  default     = "ami-0694d931cee176e7d"   # eu-west-1 Ubuntu 22.04
}

variable "key_pair_name" {
  description = "EC2 key pair for SSH access"
  type        = string
  default     = "hotelos-keypair"
}

variable "admin_cidr" {
  description = "Your IP/CIDR allowed for SSH — CHANGE THIS"
  type        = string
  default     = "0.0.0.0/0"   # restrict in production!
}

variable "repo_url" {
  description = "Git repo URL for user_data bootstrap"
  type        = string
  default     = "https://github.com/cloud-erp-platform/cloud-erp-platform.git"
}

variable "instance_type_gateway" {
  description = "EC2 instance type for API Gateway (public subnet)"
  type        = string
  default     = "t3.micro"
}

variable "instance_type_service" {
  description = "EC2 instance type for ERP/CRM/WMS services (private subnet)"
  type        = string
  default     = "t3.small"
}
