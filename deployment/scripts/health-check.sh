#!/bin/bash

# ReliQuary Platform Health Check Script
# This script checks the health of the deployed ReliQuary platform

set -e  # Exit on any error

echo "🏥 Starting ReliQuary Platform Health Check"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed or not in PATH"
    exit 1
fi

# Check if the namespace exists
echo "🔍 Checking if reliquary namespace exists..."
if ! kubectl get namespace reliquary &> /dev/null; then
    echo "❌ Error: reliquary namespace not found"
    exit 1
fi

echo "✅ Namespace exists"

# Check pod status
echo "_Pods status:"
kubectl get pods -n reliquary

# Check service status
echo "Services status:"
kubectl get services -n reliquary

# Check if deployments are ready
echo "Deployment status:"
kubectl get deployments -n reliquary

# Check platform API health
echo "🌐 Checking platform API health..."
PLATFORM_POD=$(kubectl get pods -n reliquary -l app=reliquary-platform,component=api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$PLATFORM_POD" ]; then
    echo "   Platform pod found: $PLATFORM_POD"
    # Check if pod is running
    POD_STATUS=$(kubectl get pod $PLATFORM_POD -n reliquary -o jsonpath='{.status.phase}' 2>/dev/null)
    if [ "$POD_STATUS" = "Running" ]; then
        echo "✅ Platform pod is running"
        # Try to check health endpoint (if port forwarding is available)
        echo "   Note: To check API health endpoint, run:"
        echo "   kubectl port-forward -n reliquary $PLATFORM_POD 8000:8000"
        echo "   Then visit: http://localhost:8000/health"
    else
        echo "⚠️  Platform pod is not running (status: $POD_STATUS)"
    fi
else
    echo "⚠️  No platform pod found"
fi

# Check agent orchestrator health
echo "🤖 Checking agent orchestrator health..."
AGENT_POD=$(kubectl get pods -n reliquary -l app=reliquary-platform,component=agents -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$AGENT_POD" ]; then
    echo "   Agent orchestrator pod found: $AGENT_POD"
    # Check if pod is running
    POD_STATUS=$(kubectl get pod $AGENT_POD -n reliquary -o jsonpath='{.status.phase}' 2>/dev/null)
    if [ "$POD_STATUS" = "Running" ]; then
        echo "✅ Agent orchestrator pod is running"
        # Try to check health endpoint (if port forwarding is available)
        echo "   Note: To check agent health endpoint, run:"
        echo "   kubectl port-forward -n reliquary $AGENT_POD 8001:8001"
        echo "   Then visit: http://localhost:8001/agents/health"
    else
        echo "⚠️  Agent orchestrator pod is not running (status: $POD_STATUS)"
    fi
else
    echo "⚠️  No agent orchestrator pod found"
fi

echo "📋 Detailed pod information:"
kubectl describe pods -n reliquary

echo "🎉 Health check completed!"