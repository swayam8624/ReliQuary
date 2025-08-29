#!/bin/bash

# ReliQuary Platform Deployment Script
# This script builds and deploys the ReliQuary platform to Kubernetes

set -e  # Exit on any error

echo "🚀 Starting ReliQuary Platform Deployment"

# Check if we're in the right directory
if [ ! -f "Dockerfile.platform" ]; then
    echo "❌ Error: Dockerfile.platform not found. Please run this script from the project root."
    exit 1
fi

echo "🔧 Checking prerequisites..."
# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create namespace if it doesn't exist
echo "🌐 Creating Kubernetes namespace..."
kubectl create namespace reliquary --dry-run=client -o yaml | kubectl apply -f -

# Build Docker images
echo "🐳 Building Docker images..."
echo "   Building platform image..."
docker build -t reliquary/platform:v5.0.0 -f Dockerfile.platform --target production .

echo "   Building agent orchestrator image..."
docker build -t reliquary/agent-orchestrator:v5.0.0 -f Dockerfile.agent-orchestrator .

# Create Kubernetes secrets (in a real deployment, you would use more secure methods)
echo "🔑 Creating Kubernetes secrets..."
kubectl create secret generic reliquary-secrets \
    --namespace=reliquary \
    --from-literal=database-url="postgresql://user:password@postgresql:5432/reliquary" \
    --from-literal=redis-url="redis://redis:6379" \
    --from-literal=jwt-secret-key="your-super-secret-jwt-key-here" \
    --from-literal=encryption-key="your-32-byte-encryption-key-here" \
    --from-literal=influxdb-token="your-influxdb-token-here" \
    --dry-run=client -o yaml | kubectl apply -f -

# Create ConfigMaps
echo "⚙️  Creating ConfigMaps..."
kubectl create configmap reliquary-config \
    --namespace=reliquary \
    --from-file=config/ \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f deployment/kubernetes/namespace-rbac.yaml
kubectl apply -f deployment/kubernetes/platform-deployment.yaml
kubectl apply -f deployment/kubernetes/services-ingress.yaml
kubectl apply -f deployment/kubernetes/monitoring-stack.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --namespace=reliquary \
    --for=condition=available \
    --timeout=300s \
    deployment/reliquary-platform

echo "✅ ReliQuary Platform deployed successfully!"

# Show deployment status
echo "📋 Deployment status:"
kubectl get pods -n reliquary
kubectl get services -n reliquary

echo "🔗 Access the platform at:"
echo "   API: http://localhost:8000"
echo "   Metrics: http://localhost:8080/metrics"
echo "   Agents: http://localhost:8001/agents"

echo "🎉 Deployment completed successfully!"
