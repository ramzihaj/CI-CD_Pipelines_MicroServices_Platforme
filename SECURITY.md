# 🔒 Guide de Sécurité - Microservices Platform

Documentation complète des fonctionnalités de sécurité implémentées.

## 📋 Table des Matières

1. [Fonctionnalités de Sécurité](#fonctionnalités-de-sécurité)
2. [Sealed Secrets](#sealed-secrets)
3. [RBAC](#rbac)
4. [Network Policies](#network-policies)
5. [Pod Security](#pod-security)
6. [TLS/SSL](#tlsssl)
7. [Runtime Security](#runtime-security)
8. [Sécurité Application](#sécurité-application)
9. [Scan de Vulnérabilités](#scan-vulnérabilités)
10. [Best Practices](#best-practices)

## 🛡️ Fonctionnalités de Sécurité Implémentées

### ✅ Couches de Sécurité

1. **Network Layer** - Isolation réseau complète
2. **Pod Security** - Contraintes strictes sur les pods
3. **RBAC** - Contrôle d'accès basé sur les rôles
4. **Secrets Management** - Chiffrement des secrets
5. **TLS/SSL** - Certificats automatiques
6. **Runtime Security** - Détection d'anomalies (Falco)
7. **Application Security** - Rate limiting, validation
8. **Vulnerability Scanning** - Scan automatique (Trivy)

## 🔐 1. Sealed Secrets

Chiffrez vos secrets avant de les stocker dans Git.

### Installation

```bash
kubectl apply -f security/sealed-secrets/sealed-secrets-controller.yaml
```

### Utilisation

```bash
# Générer des secrets sécurisés
chmod +x scripts/security/generate-secrets.sh
./scripts/security/generate-secrets.sh
```

## 👥 2. RBAC (Contrôle d'Accès)

### Rôles Disponibles

- **Developer**: Lecture + Exec dans pods
- **DevOps**: Accès complet
- **Viewer**: Lecture seule

### Appliquer

```bash
kubectl apply -f security/rbac/roles.yaml
```

## 🌐 3. Network Policies

Isolation réseau stricte - DENY ALL par défaut.

### Architecture

```
Internet → Frontend → Backend → Database/Redis
          ❌ Direct access to DB blocked
```

### Appliquer

```bash
kubectl apply -f security/network-policies/advanced-network-policies.yaml
```

### Règles

- Frontend peut communiquer avec Backend uniquement
- Backend peut accéder à PostgreSQL et Redis
- Database/Redis isolés de l'extérieur
- DNS autorisé pour tous

## 🛡️ 4. Pod Security

### Contraintes de Sécurité

```yaml
# Pods doivent:
- runAsNonRoot: true
- readOnlyRootFilesystem: true
- allowPrivilegeEscalation: false
- Drop ALL capabilities
```

### Appliquer

```bash
kubectl apply -f security/policies/pod-security-policy.yaml
```

## 🔒 5. TLS/SSL (Cert-Manager)

Certificats SSL automatiques avec Let's Encrypt.

### Installation

```bash
# Installer cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Appliquer la configuration
kubectl apply -f security/cert-manager/cert-manager-setup.yaml
```

### Configuration

Modifier `security/cert-manager/cert-manager-setup.yaml`:
```yaml
email: votre-email@example.com
dnsNames:
  - votre-domaine.com
```

## 🚨 6. Runtime Security (Falco)

Détection d'anomalies en temps réel.

### Installation

```bash
kubectl apply -f security/falco/falco-config.yaml
```

### Alertes Détectées

- Processus non autorisés
- Lecture de fichiers sensibles (/etc/shadow)
- Connexions sortantes suspectes
- Tentatives d'escalade de privilèges
- Modifications de fichiers système

### Voir les Alertes

```bash
kubectl logs -f daemonset/falco -n falco
```

## 🔐 7. Sécurité Application (Backend)

### Fonctionnalités Implémentées

#### Rate Limiting
```python
@rate_limit(max_requests=100, window=60)
def my_endpoint():
    pass
```

#### Validation des Entrées
- Email validation
- Username sanitization
- SQL injection detection
- XSS prevention

#### Headers de Sécurité
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security
- Content-Security-Policy

#### Détection d'Attaques
- SQL Injection
- XSS
- CSRF
- Large request protection

### Utilisation

Les middlewares sont automatiquement appliqués à toutes les routes.

## 🔍 8. Scan de Vulnérabilités

### Trivy Scanner

```bash
# Scanner tout le projet
chmod +x scripts/security/scan-vulnerabilities.sh
./scripts/security/scan-vulnerabilities.sh
```

### Scans Effectués

1. **Code source** - Vulnérabilités dans le code
2. **Images Docker** - CVEs dans les images
3. **Dépendances** - Python requirements.txt, package.json
4. **Manifests K8s** - Misconfigurations

### CI/CD Integration

Les pipelines Jenkins et GitLab incluent déjà le scan Trivy.

## 📝 Best Practices

### 1. Secrets

❌ **NE JAMAIS** :
```bash
# Hardcoder des secrets
password = "mypassword123"

# Committer des secrets dans Git
git add .env
```

✅ **TOUJOURS** :
```bash
# Utiliser des variables d'environnement
password = os.getenv('DB_PASSWORD')

# Utiliser Sealed Secrets pour K8s
kubeseal -f secret.yaml -w sealed-secret.yaml
```

### 2. Images Docker

✅ **Bonnes Pratiques** :
- Utiliser des images officielles
- Spécifier des versions exactes (pas `:latest`)
- Scanner avec Trivy avant déploiement
- Utiliser multi-stage builds
- Pas de secrets dans les images

### 3. RBAC

✅ **Principe du Moindre Privilège** :
```bash
# Donner uniquement les permissions nécessaires
# Éviter les ClusterRoleBinding globaux
# Utiliser des ServiceAccounts dédiés par pod
```

### 4. Network Policies

✅ **Deny All par Défaut** :
```yaml
# Bloquer tout, puis autoriser spécifiquement
policyTypes:
  - Ingress
  - Egress
```

### 5. Monitoring

✅ **Surveiller** :
- Logs d'accès suspects
- Tentatives d'authentification échouées
- Pics de trafic anormaux
- Alertes Falco
- Vulnérabilités Trivy

## 🚀 Déploiement Sécurisé

### Checklist Avant Production

- [ ] Secrets chiffrés avec Sealed Secrets
- [ ] RBAC configuré (pas d'admin global)
- [ ] Network Policies appliquées
- [ ] Pod Security Policies activées
- [ ] TLS/SSL configuré (HTTPS)
- [ ] Falco installé et configuré
- [ ] Scan Trivy passé (0 HIGH/CRITICAL)
- [ ] Rate limiting activé
- [ ] Logs centralisés
- [ ] Monitoring configuré
- [ ] Backups automatiques
- [ ] Disaster Recovery plan

### Commande de Déploiement Sécurisé

```bash
# 1. Scanner les vulnérabilités
./scripts/security/scan-vulnerabilities.sh

# 2. Générer des secrets sécurisés
./scripts/security/generate-secrets.sh

# 3. Appliquer les policies de sécurité
kubectl apply -f security/rbac/
kubectl apply -f security/policies/
kubectl apply -f security/network-policies/

# 4. Déployer l'application
helm install microservices-app ./helm/microservices-app \
  --set backend.image.tag=<version-scannée> \
  --namespace microservices

# 5. Activer Falco
kubectl apply -f security/falco/

# 6. Vérifier
kubectl get networkpolicies -n microservices
kubectl get psp
kubectl get pods -n microservices
```

## 🆘 Incident Response

### En Cas de Breach

1. **Isoler** - Appliquer network policy deny-all
2. **Investiguer** - Consulter logs Falco
3. **Contenir** - Bloquer IPs suspectes
4. **Éradiquer** - Patcher la vulnérabilité
5. **Récupérer** - Restaurer depuis backup
6. **Leçons** - Post-mortem et amélioration

### Commandes Utiles

```bash
# Bloquer tout le trafic vers un pod
kubectl label pod <pod-name> isolated=true -n microservices

# Voir les alertes Falco
kubectl logs -n falco daemonset/falco | grep CRITICAL

# Voir les tentatives de connexion
kubectl logs -n microservices deployment/backend | grep "401\|403"

# Exporter les logs pour analyse
kubectl logs -n microservices --all-containers=true > incident.log
```

## 📚 Ressources

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [Falco Rules](https://falco.org/docs/rules/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

## 🔄 Mises à Jour

Vérifier régulièrement :
- Mises à jour de sécurité Kubernetes
- CVEs dans les images Docker
- Dépendances Python/Node.js
- Règles Falco

```bash
# Scanner hebdomadairement
crontab -e
0 2 * * 1 cd /path/to/project && ./scripts/security/scan-vulnerabilities.sh
```

---

**Sécurité = Processus Continu, pas un État Final** 🔒
