#!/bin/bash

# Script de scan de vulnérabilités avec Trivy
# Usage: ./scan-vulnerabilities.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Scan de vulnérabilités avec Trivy...${NC}\n"

# Vérifier si Trivy est installé
if ! command -v trivy &> /dev/null; then
    echo -e "${RED}❌ Trivy n'est pas installé${NC}"
    echo "Installation: https://aquasecurity.github.io/trivy/"
    exit 1
fi

# Scanner les images Docker
scan_image() {
    local image=$1
    echo -e "\n${YELLOW}Scan de $image...${NC}"
    trivy image --severity HIGH,CRITICAL --exit-code 0 $image
}

# Scanner le code source
echo -e "${YELLOW}Scan du code source...${NC}"
trivy fs --severity HIGH,CRITICAL .

# Scanner les images
echo -e "\n${YELLOW}Scan des images Docker...${NC}"

# Backend
if docker images | grep -q "backend"; then
    scan_image "backend:latest"
fi

# Frontend
if docker images | grep -q "frontend"; then
    scan_image "frontend:latest"
fi

# Scanner les manifests Kubernetes
echo -e "\n${YELLOW}Scan des manifests Kubernetes...${NC}"
trivy config --severity HIGH,CRITICAL k8s/

# Scanner les dépendances Python
echo -e "\n${YELLOW}Scan des dépendances Python...${NC}"
if [ -f "backend/requirements.txt" ]; then
    trivy fs --severity HIGH,CRITICAL backend/requirements.txt
fi

# Scanner les dépendances Node.js
echo -e "\n${YELLOW}Scan des dépendances Node.js...${NC}"
if [ -f "frontend/package.json" ]; then
    trivy fs --severity HIGH,CRITICAL frontend/
fi

echo -e "\n${GREEN}✅ Scan terminé!${NC}"
