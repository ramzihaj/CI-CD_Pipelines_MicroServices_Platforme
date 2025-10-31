#!/bin/bash

# Script de génération de secrets sécurisés pour Kubernetes
# Usage: ./generate-secrets.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔐 Génération des secrets sécurisés...${NC}\n"

# Générer une clé secrète aléatoire
generate_secret() {
    openssl rand -base64 32
}

# Générer un mot de passe fort
generate_password() {
    openssl rand -base64 24 | tr -d "=+/" | cut -c1-20
}

# Créer le secret pour l'application
echo -e "${YELLOW}Création du secret application...${NC}"
kubectl create secret generic app-secrets \
    --from-literal=secret-key=$(generate_secret) \
    --namespace=microservices \
    --dry-run=client -o yaml > k8s/backend/app-secrets.yaml

# Créer le secret PostgreSQL
echo -e "${YELLOW}Création du secret PostgreSQL...${NC}"
DB_PASSWORD=$(generate_password)
kubectl create secret generic postgres-secret \
    --from-literal=POSTGRES_DB=microservices \
    --from-literal=POSTGRES_USER=postgres \
    --from-literal=POSTGRES_PASSWORD=$DB_PASSWORD \
    --namespace=microservices \
    --dry-run=client -o yaml > k8s/database/postgres-secret-generated.yaml

# Créer le secret Grafana
echo -e "${YELLOW}Création du secret Grafana...${NC}"
GRAFANA_PASSWORD=$(generate_password)
kubectl create secret generic grafana-secrets \
    --from-literal=admin-password=$GRAFANA_PASSWORD \
    --namespace=monitoring \
    --dry-run=client -o yaml > monitoring/grafana/grafana-secrets-generated.yaml

echo -e "\n${GREEN}✅ Secrets générés avec succès!${NC}"
echo -e "\n${YELLOW}⚠️  IMPORTANT: Sauvegardez ces mots de passe:${NC}"
echo -e "PostgreSQL: $DB_PASSWORD"
echo -e "Grafana: $GRAFANA_PASSWORD"
echo -e "\n${YELLOW}Les fichiers générés sont dans:${NC}"
echo -e "- k8s/backend/app-secrets.yaml"
echo -e "- k8s/database/postgres-secret-generated.yaml"
echo -e "- monitoring/grafana/grafana-secrets-generated.yaml"
echo -e "\n${YELLOW}⚠️  NE COMMITTEZ PAS CES FICHIERS DANS GIT!${NC}"
