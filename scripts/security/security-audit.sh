#!/bin/bash

# Script d'audit de sécurité complet
# Usage: ./security-audit.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Audit de Sécurité - Microservices Platform${NC}\n"

# Score de sécurité
SCORE=0
TOTAL_CHECKS=10

check_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    SCORE=$((SCORE + 1))
}

check_fail() {
    echo -e "${RED}✗ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 1. Vérifier les Network Policies
echo -e "\n${YELLOW}[1/10] Network Policies${NC}"
if kubectl get networkpolicies -n microservices &> /dev/null; then
    NP_COUNT=$(kubectl get networkpolicies -n microservices --no-headers 2>/dev/null | wc -l)
    if [ "$NP_COUNT" -gt 0 ]; then
        check_pass "Network Policies actives: $NP_COUNT"
    else
        check_fail "Aucune Network Policy trouvée"
    fi
else
    check_warn "Namespace microservices non trouvé"
fi

# 2. Vérifier RBAC
echo -e "\n${YELLOW}[2/10] RBAC Configuration${NC}"
if kubectl get roles -n microservices &> /dev/null; then
    ROLE_COUNT=$(kubectl get roles -n microservices --no-headers 2>/dev/null | wc -l)
    if [ "$ROLE_COUNT" -gt 0 ]; then
        check_pass "Roles RBAC configurés: $ROLE_COUNT"
    else
        check_fail "Aucun rôle RBAC trouvé"
    fi
else
    check_warn "Impossible de vérifier RBAC"
fi

# 3. Vérifier les Secrets
echo -e "\n${YELLOW}[3/10] Secrets Management${NC}"
if kubectl get secrets -n microservices &> /dev/null; then
    SECRET_COUNT=$(kubectl get secrets -n microservices --no-headers 2>/dev/null | wc -l)
    if [ "$SECRET_COUNT" -gt 0 ]; then
        check_pass "Secrets Kubernetes: $SECRET_COUNT"
    else
        check_warn "Aucun secret trouvé"
    fi
else
    check_warn "Namespace microservices non trouvé"
fi

# 4. Vérifier TLS/SSL
echo -e "\n${YELLOW}[4/10] TLS/SSL Configuration${NC}"
if kubectl get certificates -n microservices &> /dev/null; then
    check_pass "Cert-Manager installé"
else
    check_warn "Cert-Manager non installé"
fi

# 5. Vérifier Pod Security
echo -e "\n${YELLOW}[5/10] Pod Security${NC}"
PRIVILEGED=$(kubectl get pods -n microservices -o json 2>/dev/null | grep -c '"privileged": true' || echo "0")
if [ "$PRIVILEGED" -eq 0 ]; then
    check_pass "Aucun pod privilégié détecté"
else
    check_fail "$PRIVILEGED pods privilégiés trouvés"
fi

# 6. Vérifier les images
echo -e "\n${YELLOW}[6/10] Container Images${NC}"
LATEST_TAGS=$(kubectl get pods -n microservices -o json 2>/dev/null | grep -c '"image":.*:latest' || echo "0")
if [ "$LATEST_TAGS" -eq 0 ]; then
    check_pass "Aucune image :latest utilisée"
else
    check_warn "$LATEST_TAGS pods utilisent le tag :latest"
fi

# 7. Vérifier les ressources limits
echo -e "\n${YELLOW}[7/10] Resource Limits${NC}"
NO_LIMITS=$(kubectl get pods -n microservices -o json 2>/dev/null | grep -c '"limits": {}' || echo "0")
if [ "$NO_LIMITS" -eq 0 ]; then
    check_pass "Tous les pods ont des resource limits"
else
    check_warn "$NO_LIMITS pods sans resource limits"
fi

# 8. Vérifier Falco
echo -e "\n${YELLOW}[8/10] Runtime Security (Falco)${NC}"
if kubectl get daemonset falco -n falco &> /dev/null; then
    check_pass "Falco installé et actif"
else
    check_warn "Falco non installé"
fi

# 9. Vérifier les Service Accounts
echo -e "\n${YELLOW}[9/10] Service Accounts${NC}"
DEFAULT_SA=$(kubectl get pods -n microservices -o json 2>/dev/null | grep -c '"serviceAccount": "default"' || echo "0")
if [ "$DEFAULT_SA" -eq 0 ]; then
    check_pass "Service Accounts dédiés utilisés"
else
    check_warn "$DEFAULT_SA pods utilisent le SA 'default'"
fi

# 10. Vérifier les volumes read-only
echo -e "\n${YELLOW}[10/10] Read-Only Filesystems${NC}"
RO_ROOT=$(kubectl get pods -n microservices -o json 2>/dev/null | grep -c '"readOnlyRootFilesystem": true' || echo "0")
if [ "$RO_ROOT" -gt 0 ]; then
    check_pass "$RO_ROOT pods avec root filesystem read-only"
else
    check_warn "Aucun pod avec root filesystem read-only"
fi

# Calculer le score final
echo -e "\n${YELLOW}════════════════════════════${NC}"
PERCENTAGE=$((SCORE * 100 / TOTAL_CHECKS))

if [ "$PERCENTAGE" -ge 80 ]; then
    echo -e "${GREEN}Score de Sécurité: $SCORE/$TOTAL_CHECKS ($PERCENTAGE%)${NC}"
    echo -e "${GREEN}✅ Excellent niveau de sécurité!${NC}"
elif [ "$PERCENTAGE" -ge 60 ]; then
    echo -e "${YELLOW}Score de Sécurité: $SCORE/$TOTAL_CHECKS ($PERCENTAGE%)${NC}"
    echo -e "${YELLOW}⚠️  Bon niveau, quelques améliorations possibles${NC}"
else
    echo -e "${RED}Score de Sécurité: $SCORE/$TOTAL_CHECKS ($PERCENTAGE%)${NC}"
    echo -e "${RED}❌ Niveau de sécurité insuffisant!${NC}"
fi

echo -e "\n${YELLOW}Recommandations:${NC}"
echo "1. Appliquer les Network Policies: kubectl apply -f security/network-policies/"
echo "2. Configurer RBAC: kubectl apply -f security/rbac/"
echo "3. Installer Cert-Manager pour TLS"
echo "4. Déployer Falco pour Runtime Security"
echo "5. Utiliser Sealed Secrets pour les secrets"
echo ""
echo "Pour plus de détails: cat SECURITY.md"
