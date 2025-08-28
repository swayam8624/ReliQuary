#!/bin/bash

# ReliQuary Platform Production Deployment Script
# Version: 5.0.0
# Description: Complete deployment script for ReliQuary enterprise platform

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_DIR="${PROJECT_ROOT}/deployment"

# Default values
ENVIRONMENT=${ENVIRONMENT:-production}
AWS_REGION=${AWS_REGION:-us-west-2}
CLUSTER_NAME=${CLUSTER_NAME:-reliquary-production}
NAMESPACE=${NAMESPACE:-reliquary}
IMAGE_TAG=${IMAGE_TAG:-v5.0.0}
DRY_RUN=${DRY_RUN:-false}
SKIP_INFRASTRUCTURE=${SKIP_INFRASTRUCTURE:-false}
SKIP_MONITORING=${SKIP_MONITORING:-false}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check required tools
    command -v aws >/dev/null 2>&1 || missing_tools+=("aws-cli")
    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    command -v terraform >/dev/null 2>&1 || missing_tools+=("terraform")
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install the missing tools and try again."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Kubernetes access
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_warning "Kubernetes cluster not accessible. Will attempt to configure kubeconfig."
    fi
    
    print_success "Prerequisites check completed"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    if [ "$SKIP_INFRASTRUCTURE" = "true" ]; then
        print_status "Skipping infrastructure deployment"
        return 0
    fi
    
    print_status "Deploying infrastructure with Terraform..."
    
    cd "${DEPLOYMENT_DIR}/terraform"
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning infrastructure deployment..."
    terraform plan -var="environment=${ENVIRONMENT}" \
                   -var="aws_region=${AWS_REGION}" \
                   -var="cluster_name=${CLUSTER_NAME}" \
                   -out=tfplan
    
    if [ "$DRY_RUN" = "true" ]; then
        print_status "Dry run mode - skipping infrastructure deployment"
        return 0
    fi
    
    # Apply deployment
    print_status "Applying infrastructure deployment..."
    terraform apply tfplan
    
    # Update kubeconfig
    print_status "Updating kubeconfig..."
    aws eks update-kubeconfig --region "${AWS_REGION}" --name "${CLUSTER_NAME}"
    
    print_success "Infrastructure deployment completed"
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    cd "${PROJECT_ROOT}"
    
    # Build platform image
    print_status "Building platform image..."
    docker build -f Dockerfile.platform -t "reliquary/platform:${IMAGE_TAG}" .
    docker tag "reliquary/platform:${IMAGE_TAG}" "reliquary/platform:latest"
    
    # Build agent orchestrator image
    print_status "Building agent orchestrator image..."
    docker build -f Dockerfile.agent-orchestrator -t "reliquary/agent-orchestrator:${IMAGE_TAG}" .
    docker tag "reliquary/agent-orchestrator:${IMAGE_TAG}" "reliquary/agent-orchestrator:latest"
    
    if [ "$DRY_RUN" = "false" ]; then
        # Push images (assuming registry is configured)
        print_status "Pushing images to registry..."
        docker push "reliquary/platform:${IMAGE_TAG}"
        docker push "reliquary/platform:latest"
        docker push "reliquary/agent-orchestrator:${IMAGE_TAG}"
        docker push "reliquary/agent-orchestrator:latest"
    fi
    
    print_success "Docker images built and pushed"
}

# Function to deploy monitoring stack
deploy_monitoring() {
    if [ "$SKIP_MONITORING" = "true" ]; then
        print_status "Skipping monitoring deployment"
        return 0
    fi
    
    print_status "Deploying monitoring stack..."
    
    # Create monitoring namespace
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy monitoring components
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/monitoring-stack.yaml"
    
    # Wait for monitoring to be ready
    print_status "Waiting for monitoring stack to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s
    
    print_success "Monitoring stack deployed"
}

# Function to deploy ReliQuary platform
deploy_platform() {
    print_status "Deploying ReliQuary platform..."
    
    # Create namespace
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply RBAC and configurations
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/namespace-rbac.yaml"
    
    # Deploy services and ingress
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/services-ingress.yaml"
    
    # Update platform deployment with correct image tag
    sed "s/v5\.0\.0/${IMAGE_TAG}/g" "${DEPLOYMENT_DIR}/kubernetes/platform-deployment.yaml" | kubectl apply -f -
    
    # Wait for deployment to be ready
    print_status "Waiting for platform deployment to be ready..."
    kubectl wait --for=condition=ready pod -l app=reliquary-platform -n "${NAMESPACE}" --timeout=600s
    
    print_success "ReliQuary platform deployed"
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check pod status
    print_status "Checking pod status..."
    kubectl get pods -n "${NAMESPACE}" -l app=reliquary-platform
    
    # Check service endpoints
    print_status "Checking service endpoints..."
    kubectl get svc -n "${NAMESPACE}"
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    kubectl port-forward -n "${NAMESPACE}" svc/reliquary-platform-service 8080:80 &
    PORT_FORWARD_PID=$!
    sleep 5
    
    if curl -f http://localhost:8080/health >/dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
    fi
    
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    print_success "Health checks completed"
}

# Function to deploy with Helm (alternative deployment method)
deploy_with_helm() {
    print_status "Deploying with Helm..."
    
    cd "${DEPLOYMENT_DIR}/helm"
    
    # Update Helm dependencies
    helm dependency update
    
    # Deploy with Helm
    helm upgrade --install reliquary . \
        --namespace "${NAMESPACE}" \
        --create-namespace \
        --values values.yaml \
        --set "image.platform.tag=${IMAGE_TAG}" \
        --set "image.agentOrchestrator.tag=${IMAGE_TAG}" \
        --set "app.environment=${ENVIRONMENT}" \
        --wait --timeout=20m
    
    print_success "Helm deployment completed"
}

# Function to run post-deployment configuration
post_deployment_config() {
    print_status "Running post-deployment configuration..."
    
    # Apply security policies
    print_status "Applying security policies..."
    kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: reliquary-network-policy
  namespace: ${NAMESPACE}
spec:
  podSelector:
    matchLabels:
      app: reliquary-platform
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ${NAMESPACE}
    ports:
    - protocol: TCP
      port: 8000
EOF
    
    # Configure resource quotas
    print_status "Configuring resource quotas..."
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: reliquary-quota
  namespace: ${NAMESPACE}
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
EOF
    
    print_success "Post-deployment configuration completed"
}

# Function to setup monitoring dashboards
setup_monitoring_dashboards() {
    print_status "Setting up monitoring dashboards..."
    
    # Apply Grafana dashboard configurations
    python3 "${PROJECT_ROOT}/observability/grafana_dashboards.py"
    
    # Configure Prometheus rules
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-reliquary-rules
  namespace: monitoring
data:
  reliquary.rules: |
    groups:
    - name: reliquary.rules
      rules:
      - alert: ReliQuaryHighCPU
        expr: reliquary_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
      - alert: ReliQuaryHighMemory
        expr: reliquary_memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
EOF
    
    print_success "Monitoring dashboards configured"
}

# Function to cleanup on failure
cleanup_on_failure() {
    print_error "Deployment failed. Starting cleanup..."
    
    # Remove failed deployments
    kubectl delete deployment reliquary-platform -n "${NAMESPACE}" --ignore-not-found=true
    
    # Remove services
    kubectl delete svc reliquary-platform-service -n "${NAMESPACE}" --ignore-not-found=true
    
    print_warning "Cleanup completed. Check logs for error details."
}

# Function to show deployment summary
show_deployment_summary() {
    print_success "=== ReliQuary Deployment Summary ==="
    echo
    print_status "Environment: ${ENVIRONMENT}"
    print_status "AWS Region: ${AWS_REGION}"
    print_status "Cluster: ${CLUSTER_NAME}"
    print_status "Namespace: ${NAMESPACE}"
    print_status "Image Tag: ${IMAGE_TAG}"
    echo
    
    print_status "Deployment URLs:"
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  API: https://api.reliquary.io"
        echo "  Platform: https://platform.reliquary.io"
        echo "  Grafana: https://grafana.reliquary.io"
        echo "  Prometheus: https://prometheus.reliquary.io"
    else
        echo "  Use kubectl port-forward to access services locally"
    fi
    echo
    
    print_status "Useful commands:"
    echo "  kubectl get pods -n ${NAMESPACE}"
    echo "  kubectl logs -f deployment/reliquary-platform -n ${NAMESPACE}"
    echo "  kubectl port-forward -n ${NAMESPACE} svc/reliquary-platform-service 8080:80"
    echo
    
    print_success "Deployment completed successfully!"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -e, --environment ENV     Deployment environment (default: production)"
    echo "  -r, --region REGION       AWS region (default: us-west-2)"
    echo "  -c, --cluster NAME        EKS cluster name (default: reliquary-production)"
    echo "  -n, --namespace NAME      Kubernetes namespace (default: reliquary)"
    echo "  -t, --tag TAG             Docker image tag (default: v5.0.0)"
    echo "  -d, --dry-run             Perform dry run without applying changes"
    echo "  --skip-infra             Skip infrastructure deployment"
    echo "  --skip-monitoring        Skip monitoring stack deployment"
    echo "  --helm                   Use Helm for deployment"
    echo "  -h, --help               Show this help message"
    echo
    echo "Examples:"
    echo "  $0                                    # Deploy to production"
    echo "  $0 -e staging -t v5.0.0-rc1         # Deploy to staging with RC tag"
    echo "  $0 --dry-run                        # Perform dry run"
    echo "  $0 --helm                           # Deploy using Helm"
}

# Main deployment function
main() {
    local use_helm=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -c|--cluster)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-infra)
                SKIP_INFRASTRUCTURE=true
                shift
                ;;
            --skip-monitoring)
                SKIP_MONITORING=true
                shift
                ;;
            --helm)
                use_helm=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    print_status "Starting ReliQuary deployment..."
    print_status "Environment: ${ENVIRONMENT}"
    print_status "Dry run: ${DRY_RUN}"
    
    # Execute deployment steps
    check_prerequisites
    deploy_infrastructure
    build_and_push_images
    deploy_monitoring
    
    if [ "$use_helm" = "true" ]; then
        deploy_with_helm
    else
        deploy_platform
    fi
    
    post_deployment_config
    setup_monitoring_dashboards
    run_health_checks
    show_deployment_summary
}

# Run main function
main "$@"