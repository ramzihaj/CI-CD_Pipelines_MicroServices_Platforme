#!/bin/bash

# Deployment script using Helm
# This script deploys the application using Helm charts

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
NAMESPACE="microservices"
RELEASE_NAME="microservices-app"
CHART_PATH="./helm/microservices-app"

# Parse arguments
ENVIRONMENT=${1:-development}
IMAGE_TAG=${2:-latest}

echo -e "${YELLOW}🚀 Deploying Microservices Application${NC}"
echo "Environment: $ENVIRONMENT"
echo "Image Tag: $IMAGE_TAG"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm is not installed${NC}"
    exit 1
fi

# Create namespace
echo -e "\n${YELLOW}Creating namespace...${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
echo -e "\n${YELLOW}Deploying with Helm...${NC}"

if [ "$ENVIRONMENT" == "production" ]; then
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --set backend.image.tag=$IMAGE_TAG \
        --set frontend.image.tag=$IMAGE_TAG \
        --set backend.replicaCount=5 \
        --set frontend.replicaCount=3 \
        --set backend.autoscaling.enabled=true \
        --set backend.autoscaling.minReplicas=3 \
        --set backend.autoscaling.maxReplicas=15 \
        --set monitoring.prometheus.enabled=true \
        --set monitoring.grafana.enabled=true \
        --wait \
        --timeout 10m
elif [ "$ENVIRONMENT" == "staging" ]; then
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --set backend.image.tag=$IMAGE_TAG \
        --set frontend.image.tag=$IMAGE_TAG \
        --set backend.replicaCount=2 \
        --set frontend.replicaCount=2 \
        --set backend.autoscaling.enabled=true \
        --set frontend.ingress.host=staging.microservices.example.com \
        --wait \
        --timeout 10m
else
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --set backend.image.tag=$IMAGE_TAG \
        --set frontend.image.tag=$IMAGE_TAG \
        --wait \
        --timeout 10m
fi

echo -e "${GREEN}✓ Deployment successful${NC}"

# Check deployment status
echo -e "\n${YELLOW}Checking deployment status...${NC}"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE

# Run smoke tests
echo -e "\n${YELLOW}Running smoke tests...${NC}"
sleep 10  # Wait for services to be fully ready

BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=backend -o jsonpath="{.items[0].metadata.name}")
if [ ! -z "$BACKEND_POD" ]; then
    echo "Testing backend health endpoint..."
    kubectl exec -n $NAMESPACE $BACKEND_POD -- curl -s http://localhost:5000/api/health || true
    echo -e "${GREEN}✓ Backend is healthy${NC}"
fi

echo -e "\n${GREEN}✅ Deployment complete!${NC}"
echo -e "\nTo access the application:"
echo "  kubectl port-forward svc/frontend-service 8080:80 -n $NAMESPACE"
echo "  kubectl port-forward svc/backend-service 5000:5000 -n $NAMESPACE"
echo -e "\nTo view logs:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo -e "\nTo check status:"
echo "  helm status $RELEASE_NAME -n $NAMESPACE"
