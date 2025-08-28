# ReliQuary Platform Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the ReliQuary enterprise platform to production using Kubernetes, with complete CI/CD pipelines, monitoring, and security configurations.

## Architecture

The ReliQuary platform is deployed as a microservices architecture on Kubernetes with the following components:

### Core Services

- **Platform API**: Main application server (FastAPI)
- **Agent Orchestrator**: Multi-agent consensus coordinator
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage

### Monitoring Stack

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Jaeger**: Distributed tracing
- **InfluxDB**: Time-series data storage

### Infrastructure

- **AWS EKS**: Managed Kubernetes cluster
- **Application Load Balancer**: Ingress traffic management
- **AWS RDS**: Managed PostgreSQL
- **ElastiCache**: Managed Redis
- **S3**: Object storage for backups and artifacts

## Prerequisites

### Required Tools

- AWS CLI v2.x
- kubectl v1.27+
- Helm v3.12+
- Terraform v1.5+
- Docker v20.10+

### AWS Permissions

Your AWS credentials need the following permissions:

- EKS cluster management
- EC2 instance management
- VPC and networking
- RDS and ElastiCache
- S3 bucket management
- IAM role management

### Installation

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### 2. Clone and Setup

```bash
git clone https://github.com/reliquary/platform.git
cd platform
```

### 3. Deploy Infrastructure

```bash
# Deploy full stack to production
./deployment/scripts/deploy.sh

# Deploy to staging
./deployment/scripts/deploy.sh --environment staging

# Dry run to see what would be deployed
./deployment/scripts/deploy.sh --dry-run
```

## Detailed Deployment Process

### Step 1: Infrastructure Deployment with Terraform

```bash
cd deployment/terraform

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan -var="environment=production" -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

This creates:

- VPC with public/private subnets across 3 AZs
- EKS cluster with managed node groups
- RDS PostgreSQL instance with encryption
- ElastiCache Redis cluster
- S3 buckets for data and backups
- IAM roles and security groups

### Step 2: Configure Kubernetes Access

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name reliquary-production

# Verify access
kubectl cluster-info
```

### Step 3: Deploy Core Services

```bash
# Create namespaces and RBAC
kubectl apply -f deployment/kubernetes/namespace-rbac.yaml

# Deploy PostgreSQL and Redis
kubectl apply -f deployment/kubernetes/services-ingress.yaml

# Deploy monitoring stack
kubectl apply -f deployment/kubernetes/monitoring-stack.yaml
```

### Step 4: Build and Deploy Application

```bash
# Build Docker images
docker build -f Dockerfile.platform -t reliquary/platform:v5.0.0 .
docker build -f Dockerfile.agent-orchestrator -t reliquary/agent-orchestrator:v5.0.0 .

# Deploy application
kubectl apply -f deployment/kubernetes/platform-deployment.yaml
```

### Step 5: Configure Ingress and SSL

```bash
# Install nginx-ingress controller
helm install nginx-ingress ingress-nginx/ingress-nginx

# Install cert-manager for SSL certificates
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Apply ingress configuration
kubectl apply -f deployment/kubernetes/services-ingress.yaml
```

## Helm Deployment (Alternative)

For simplified deployment management, use Helm:

```bash
cd deployment/helm

# Deploy with Helm
helm install reliquary . \
  --namespace reliquary \
  --create-namespace \
  --values values.yaml \
  --set image.platform.tag=v5.0.0 \
  --wait
```

## Configuration

### Environment Variables

| Variable              | Description                  | Default                         |
| --------------------- | ---------------------------- | ------------------------------- |
| `ENVIRONMENT`         | Deployment environment       | `production`                    |
| `DATABASE_URL`        | PostgreSQL connection string | From secret                     |
| `REDIS_URL`           | Redis connection string      | From secret                     |
| `JWT_SECRET_KEY`      | JWT signing key              | From secret                     |
| `PROMETHEUS_ENDPOINT` | Prometheus server URL        | `http://prometheus:9090`        |
| `JAEGER_ENDPOINT`     | Jaeger collector URL         | `http://jaeger-collector:14268` |

### Secrets Management

Secrets are stored in Kubernetes secrets and should be updated with production values:

```bash
# Update database password
kubectl create secret generic reliquary-secrets \
  --from-literal=database-url="postgresql://user:password@host:5432/reliquary" \
  --from-literal=redis-url="redis://redis:6379" \
  --from-literal=jwt-secret-key="your-jwt-secret" \
  --from-literal=encryption-key="your-encryption-key" \
  --namespace reliquary
```

## Monitoring and Observability

### Accessing Dashboards

```bash
# Grafana (admin/admin)
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Jaeger
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

### Key Metrics

- **System Health Score**: Overall platform health (0-1)
- **CPU Usage**: Platform and agent CPU utilization
- **Memory Usage**: Memory consumption across services
- **Consensus Operations**: Multi-agent consensus performance
- **Security Events**: Security-related events and anomalies
- **Response Times**: API response latency

### Alerts

Default alerts are configured for:

- High CPU usage (>80%)
- High memory usage (>85%)
- Consensus failure rate (>10%)
- Security event spikes
- Service unavailability

## Security

### Network Security

- Network policies restrict inter-pod communication
- All external traffic goes through ingress controller
- TLS encryption for all external endpoints
- Private subnets for database and cache

### Data Encryption

- Encryption at rest for all storage (PostgreSQL, Redis, S3)
- Encryption in transit with TLS 1.3
- Kubernetes secrets encryption with AWS KMS

### Access Control

- RBAC for Kubernetes access
- IAM roles for AWS resource access
- Service accounts with minimal permissions
- Pod security standards enforced

## Backup and Disaster Recovery

### Automated Backups

```bash
# PostgreSQL backups (daily at 2 AM)
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgresql-backup
  namespace: reliquary
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15-alpine
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgresql -U reliquary_user reliquary > /backup/reliquary-\$(date +%Y%m%d-%H%M%S).sql
              aws s3 cp /backup/ s3://reliquary-backups/ --recursive
EOF
```

### Disaster Recovery

1. **RDS Point-in-Time Recovery**: 30-day backup retention
2. **Cross-Region Replication**: Automated backup to secondary region
3. **Kubernetes Velero**: Cluster state backups
4. **Infrastructure as Code**: Complete infrastructure recreation with Terraform

## Scaling

### Horizontal Pod Autoscaling

```bash
# Enable HPA for platform deployment
kubectl autoscale deployment reliquary-platform \
  --cpu-percent=70 \
  --min=3 \
  --max=20 \
  --namespace reliquary
```

### Cluster Autoscaling

The EKS cluster is configured with node group autoscaling:

- Minimum nodes: 3
- Maximum nodes: 20
- Scale based on pod resource requests

### Database Scaling

- RDS read replicas for read scaling
- Connection pooling with PgBouncer
- Automated storage scaling up to 1TB

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n reliquary

# Check pod logs
kubectl logs deployment/reliquary-platform -n reliquary

# Check events
kubectl get events -n reliquary --sort-by=.metadata.creationTimestamp
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- \
  psql -h postgresql.reliquary.svc.cluster.local -U reliquary_user -d reliquary
```

#### Certificate Issues

```bash
# Check certificate status
kubectl get certificate -n reliquary

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Debugging Commands

```bash
# Port forward to service
kubectl port-forward -n reliquary svc/reliquary-platform-service 8080:80

# Exec into pod
kubectl exec -it deployment/reliquary-platform -n reliquary -- /bin/bash

# Check resource usage
kubectl top pods -n reliquary
kubectl top nodes
```

## Maintenance

### Regular Tasks

1. **Weekly**: Review monitoring dashboards and alerts
2. **Monthly**: Update container images and dependencies
3. **Quarterly**: Review and rotate secrets
4. **Annually**: Disaster recovery testing

### Updates

```bash
# Update application
helm upgrade reliquary deployment/helm \
  --namespace reliquary \
  --set image.platform.tag=v5.1.0

# Update Kubernetes cluster
aws eks update-cluster-version \
  --region us-west-2 \
  --name reliquary-production \
  --version 1.28
```

## Cost Optimization

### Resource Management

- Set appropriate resource requests and limits
- Use spot instances for non-critical workloads
- Implement cluster autoscaling
- Schedule non-production environments to shut down overnight

### Monitoring Costs

- Use AWS Cost Explorer to track spending
- Set up billing alerts for cost thresholds
- Regular review of unused resources

### Estimated Monthly Costs

| Component                        | Cost (USD) |
| -------------------------------- | ---------- |
| EKS Cluster                      | $72        |
| Worker Nodes (6x t3.large)       | $518       |
| RDS (db.r6g.large)               | $292       |
| ElastiCache (3x cache.r6g.large) | $328       |
| Load Balancers                   | $23        |
| Storage & Data Transfer          | $150       |
| **Total Estimated**              | **$1,383** |

## Support

### Documentation

- API Documentation: https://docs.reliquary.io/api
- Architecture Guide: https://docs.reliquary.io/architecture
- Security Guide: https://docs.reliquary.io/security

### Monitoring

- Platform Status: https://status.reliquary.io
- Grafana Dashboards: https://grafana.reliquary.io
- Error Tracking: Integrated with platform logging

### Emergency Contacts

- Platform Team: platform@reliquary.io
- Security Team: security@reliquary.io
- On-call: +1-XXX-XXX-XXXX

## License

ReliQuary Platform is licensed under the MIT License. See LICENSE file for details.
