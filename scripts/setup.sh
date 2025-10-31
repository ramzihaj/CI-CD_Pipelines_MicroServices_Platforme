#!/bin/bash

# Setup script for microservices application
# This script prepares the local environment for deployment

set -e

echo "🚀 Setting up Microservices Application..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ $1 is installed${NC}"
    fi
}

echo -e "\n${YELLOW}Checking required tools...${NC}"
check_tool docker
check_tool kubectl
check_tool helm
check_tool minikube

# Start Minikube if not running
echo -e "\n${YELLOW}Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
    echo -e "${GREEN}✓ Minikube started${NC}"
else
    echo -e "${GREEN}✓ Minikube is already running${NC}"
fi

# Enable required addons
echo -e "\n${YELLOW}Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server
echo -e "${GREEN}✓ Addons enabled${NC}"

# Create namespace
echo -e "\n${YELLOW}Creating namespace...${NC}"
kubectl create namespace microservices --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespaces created${NC}"

# Build Docker images
echo -e "\n${YELLOW}Building Docker images...${NC}"
eval $(minikube docker-env)

echo "Building backend image..."
docker build -t backend:latest ./backend

echo "Building frontend image..."
docker build -t frontend:latest ./frontend

echo -e "${GREEN}✓ Docker images built${NC}"

# Deploy with kubectl (alternative to Helm)
echo -e "\n${YELLOW}Deploying application...${NC}"

# Deploy database
kubectl apply -f k8s/database/postgres-secret.yaml
kubectl apply -f k8s/database/postgres-deployment.yaml
kubectl apply -f k8s/database/redis-deployment.yaml

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n microservices

# Deploy backend
kubectl apply -f k8s/backend/backend-configmap.yaml
kubectl apply -f k8s/backend/backend-deployment.yaml

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/backend -n microservices

# Deploy frontend
kubectl apply -f k8s/frontend/frontend-deployment.yaml

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n microservices

# Apply network policies
kubectl apply -f k8s/network-policy.yaml

echo -e "${GREEN}✓ Application deployed${NC}"

# Deploy monitoring
echo -e "\n${YELLOW}Deploying monitoring stack...${NC}"
kubectl apply -f monitoring/prometheus/prometheus-config.yaml
kubectl apply -f monitoring/prometheus/prometheus-deployment.yaml
kubectl apply -f monitoring/prometheus/alerts.yaml
kubectl apply -f monitoring/grafana/grafana-deployment.yaml

echo -e "${GREEN}✓ Monitoring deployed${NC}"

# Get URLs
echo -e "\n${YELLOW}Getting service URLs...${NC}"
echo -e "\n${GREEN}Application URLs:${NC}"
echo "Frontend: $(minikube service frontend-service -n microservices --url)"
echo "Backend: $(minikube service backend-service -n microservices --url)"
echo -e "\n${GREEN}Monitoring URLs:${NC}"
echo "Grafana: $(minikube service grafana -n monitoring --url)"
echo "Prometheus: $(minikube service prometheus -n monitoring --url)"

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\nTo access services, use the URLs above or run:"
echo "  minikube service frontend-service -n microservices"
echo "  minikube service grafana -n monitoring"
echo -e "\nTo view logs:"
echo "  kubectl logs -f deployment/backend -n microservices"
echo "  kubectl logs -f deployment/frontend -n microservices"
