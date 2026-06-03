output "gateway_public_ip" {
  description = "Public IP of the Nginx API Gateway — open this in your browser"
  value       = aws_instance.gateway.public_ip
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "erp_private_ip" {
  value = aws_instance.erp.private_ip
}

output "crm_private_ip" {
  value = aws_instance.crm.private_ip
}

output "wms_private_ip" {
  value = aws_instance.wms.private_ip
}
