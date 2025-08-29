# ReliQuary Platform Deployment Guide

This guide provides instructions for deploying the ReliQuary platform to a Kubernetes cluster.

## Prerequisites

Before deploying, ensure you have the following installed:

- Docker (for building images)
- kubectl (for Kubernetes management)
- A running Kubernetes cluster (local or remote)

## Deployment Steps

### 1. Build Docker Images

The platform consists of two main components:

1. **Platform API** - Main application server
2. **Agent Orchestrator** - Multi-agent consensus system

Build the Docker images using the provided Dockerfiles:

```bash
# Build platform image
docker build -t reliquary/platform:v5.0.0 -f Dockerfile.platform --target production .

# Build agent orchestrator image
docker build -t reliquary/agent-orchestrator:v5.0.0 -f Dockerfile.agent-orchestrator .
```

### 2. Deploy to Kubernetes

Use the deployment scripts to deploy to Kubernetes:

```bash
# Deploy the platform
./deployment/scripts/deploy.sh
```

Or deploy manually using the Kubernetes manifests:

```bash
# Create namespace and RBAC
kubectl apply -f deployment/kubernetes/namespace-rbac.yaml

# Create secrets (update with your actual values)
kubectl apply -f deployment/kubernetes/secrets.yaml

# Deploy the platform
kubectl apply -f deployment/kubernetes/platform-deployment.yaml

# Deploy services and ingress
kubectl apply -f deployment/kubernetes/services-ingress.yaml

# Deploy monitoring stack
kubectl apply -f deployment/kubernetes/monitoring-stack.yaml
```

### 3. Verify Deployment

Check the status of your deployment:

```bash
# Check pods
kubectl get pods -n reliquary

# Check services
kubectl get services -n reliquary

# Check logs
kubectl logs -n reliquary -l app=reliquary-platform
```

Run the health check script:

```bash
./deployment/scripts/health-check.sh
```

### 4. Access the Platform

Once deployed, you can access the platform at:

- **API**: http://localhost:8000
- **Metrics**: http://localhost:8080/metrics
- **Agents**: http://localhost:8001/agents

To access these endpoints, you may need to set up port forwarding:

```bash
# Port forward API
kubectl port-forward -n reliquary service/reliquary-platform-service 8000:8000

# Port forward metrics
kubectl port-forward -n reliquary service/reliquary-platform-service 8080:8080

# Port forward agents
kubectl port-forward -n reliquary service/reliquary-platform-service 8001:8001
```

## Configuration

The platform can be configured using Kubernetes ConfigMaps and Secrets. Key configuration options include:

- Database connection strings
- Redis connection details
- JWT secret keys
- Encryption keys
- Monitoring endpoints

## Scaling

The platform is designed to scale horizontally. You can adjust the number of replicas in the deployment manifest:

```yaml
spec:
  replicas: 3 # Adjust this number based on your needs
```

## Monitoring and Logging

The platform includes built-in monitoring endpoints and integrates with Prometheus and Grafana for metrics collection and visualization.

## Troubleshooting

Common issues and solutions:

1. **Pods stuck in Pending state**: Check resource quotas and node availability
2. **Health checks failing**: Check logs and configuration
3. **Connection refused**: Verify service configuration and network policies

For detailed troubleshooting, check the logs:

```bash
kubectl logs -n reliquary -l app=reliquary-platform
```

## Security Considerations

- Always use strong, unique secrets in production
- Enable TLS for all external communications
- Regularly update Docker images and dependencies
- Implement proper network policies
- Use RBAC for Kubernetes access control

## Backup and Recovery

Regular backups of the database and configuration are recommended. The platform includes audit logging for security events.

## Support

For support, please contact the ReliQuary development team or refer to the documentation.
