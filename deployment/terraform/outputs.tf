output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.reliquary.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.reliquary.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.reliquary.id
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = aws_nat_gateway.reliquary[*].id
}

# EKS Cluster Outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = aws_eks_cluster.reliquary.id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = aws_eks_cluster.reliquary.arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.reliquary.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = aws_eks_cluster.reliquary.vpc_config[0].cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = aws_iam_role.cluster.name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = aws_iam_role.cluster.arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.reliquary.certificate_authority[0].data
}

output "cluster_primary_security_group_id" {
  description = "The cluster primary security group ID created by the EKS cluster"
  value       = aws_eks_cluster.reliquary.vpc_config[0].cluster_security_group_id
}

# EKS Node Group Outputs
output "node_group_arn" {
  description = "Amazon Resource Name (ARN) of the EKS Node Group"
  value       = aws_eks_node_group.reliquary.arn
}

output "node_group_status" {
  description = "Status of the EKS Node Group"
  value       = aws_eks_node_group.reliquary.status
}

output "node_group_capacity_type" {
  description = "Type of capacity associated with the EKS Node Group"
  value       = aws_eks_node_group.reliquary.capacity_type
}

output "node_group_instance_types" {
  description = "Instance types associated with the EKS Node Group"
  value       = aws_eks_node_group.reliquary.instance_types
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.reliquary.endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.reliquary.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.reliquary.db_name
}

output "rds_username" {
  description = "RDS database username"
  value       = aws_db_instance.reliquary.username
  sensitive   = true
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

# ElastiCache Outputs
output "redis_endpoint" {
  description = "Redis primary endpoint"
  value       = aws_elasticache_replication_group.reliquary.primary_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = aws_elasticache_replication_group.reliquary.port
}

output "redis_reader_endpoint" {
  description = "Redis reader endpoint"
  value       = aws_elasticache_replication_group.reliquary.reader_endpoint_address
  sensitive   = true
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = aws_security_group.elasticache.id
}

# S3 Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.reliquary_data.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.reliquary_data.arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.reliquary_data.bucket_domain_name
}

# KMS Outputs
output "eks_kms_key_id" {
  description = "KMS key ID for EKS encryption"
  value       = aws_kms_key.eks.key_id
}

output "eks_kms_key_arn" {
  description = "KMS key ARN for EKS encryption"
  value       = aws_kms_key.eks.arn
}

output "rds_kms_key_id" {
  description = "KMS key ID for RDS encryption"
  value       = aws_kms_key.rds.key_id
}

output "rds_kms_key_arn" {
  description = "KMS key ARN for RDS encryption"
  value       = aws_kms_key.rds.arn
}

output "s3_kms_key_id" {
  description = "KMS key ID for S3 encryption"
  value       = aws_kms_key.s3.key_id
}

output "s3_kms_key_arn" {
  description = "KMS key ARN for S3 encryption"
  value       = aws_kms_key.s3.arn
}

# Security Group Outputs
output "node_ssh_security_group_id" {
  description = "Security group ID for SSH access to nodes"
  value       = aws_security_group.node_ssh.id
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "availability_zones" {
  description = "Availability zones used"
  value       = var.availability_zones
}

# Kubernetes Configuration
output "kubeconfig_update_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.reliquary.name}"
}

# Application URLs (to be used after deployment)
output "application_urls" {
  description = "Application URLs after deployment"
  value = {
    api_url      = "https://api.reliquary.io"
    platform_url = "https://platform.reliquary.io"
    grafana_url  = "https://grafana.reliquary.io"
    prometheus_url = "https://prometheus.reliquary.io"
    jaeger_url   = "https://jaeger.reliquary.io"
  }
}

# Connection Information
output "database_connection_info" {
  description = "Database connection information"
  value = {
    host     = aws_db_instance.reliquary.endpoint
    port     = aws_db_instance.reliquary.port
    database = aws_db_instance.reliquary.db_name
    username = aws_db_instance.reliquary.username
  }
  sensitive = true
}

output "redis_connection_info" {
  description = "Redis connection information"
  value = {
    primary_endpoint = aws_elasticache_replication_group.reliquary.primary_endpoint_address
    reader_endpoint  = aws_elasticache_replication_group.reliquary.reader_endpoint_address
    port            = aws_elasticache_replication_group.reliquary.port
  }
  sensitive = true
}

# Monitoring Information
output "monitoring_endpoints" {
  description = "Monitoring endpoints"
  value = {
    prometheus_internal = "http://prometheus.monitoring.svc.cluster.local:9090"
    grafana_internal    = "http://grafana.monitoring.svc.cluster.local:3000"
    jaeger_internal     = "http://jaeger-query.monitoring.svc.cluster.local:16686"
    influxdb_internal   = "http://influxdb.monitoring.svc.cluster.local:8086"
  }
}

# Infrastructure Cost Estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    eks_cluster      = "72.00"    # $0.10/hour
    eks_nodes        = "518.40"   # 6 x t3.large nodes
    rds_instance     = "292.32"   # db.r6g.large
    redis_cluster    = "327.60"   # 3 x cache.r6g.large
    nat_gateways     = "135.00"   # 3 x $45/month
    load_balancers   = "22.50"    # Classic LB
    storage          = "50.00"    # EBS, S3, snapshots
    data_transfer    = "100.00"   # Estimated
    total_estimated  = "1517.82"
  }
}