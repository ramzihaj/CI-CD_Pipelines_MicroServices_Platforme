# 📘 Deployment Guide

Guide détaillé pour déployer l'application microservices.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Déploiement Local (Docker Compose)](#déploiement-local-docker-compose)
3. [Déploiement sur Minikube](#déploiement-sur-minikube)
4. [Déploiement sur AWS EKS](#déploiement-sur-aws-eks)
5. [Configuration CI/CD](#configuration-cicd)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prérequis

### Outils Nécessaires

```bash
# Docker
docker --version  # >= 24.0

# Kubernetes
kubectl version --client  # >= 1.27

# Helm
helm version  # >= 3.12

# Minikube (pour local)
minikube version  # >= 1.31

# AWS CLI (pour EKS)
aws --version  # >= 2.0
```

## Déploiement Local (Docker Compose)

### Étape 1: Cloner le Projet

```bash
git clone <repository-url>
cd CI-CD_Pipelines
```

### Étape 2: Lancer avec Docker Compose

```bash
# Construire et démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Vérifier le statut
docker-compose ps
```

### Étape 3: Accéder aux Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### Commandes Utiles

```bash
# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build

# Voir les logs d'un service spécifique
docker-compose logs -f backend

# Nettoyer tout
docker-compose down -v
```

## Déploiement sur Minikube

### Étape 1: Démarrer Minikube

```bash
# Démarrer Minikube avec ressources suffisantes
minikube start --cpus=4 --memory=8192 --driver=docker

# Vérifier le statut
minikube status

# Activer les addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Étape 2: Configuration de l'Environnement Docker

```bash
# Configurer Docker pour utiliser le daemon Minikube
eval $(minikube docker-env)

# Construire les images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend
```

### Étape 3: Déploiement Automatique

```bash
# Utiliser le script de setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Étape 4: Déploiement Manuel avec kubectl

```bash
# Créer le namespace
kubectl create namespace microservices

# Déployer la base de données
kubectl apply -f k8s/database/

# Attendre que PostgreSQL soit prêt
kubectl wait --for=condition=available --timeout=300s \
  deployment/postgres -n microservices

# Déployer le backend
kubectl apply -f k8s/backend/

# Déployer le frontend
kubectl apply -f k8s/frontend/

# Appliquer les network policies
kubectl apply -f k8s/network-policy.yaml
```

### Étape 5: Déploiement avec Helm

```bash
# Mettre à jour les dépendances
helm dependency update ./helm/microservices-app

# Installer avec Helm
helm install microservices-app ./helm/microservices-app \
  --namespace microservices \
  --create-namespace \
  --values ./helm/microservices-app/values.yaml

# Vérifier le déploiement
helm status microservices-app -n microservices
```

### Étape 6: Accéder aux Services

```bash
# Obtenir les URLs
minikube service frontend-service -n microservices --url
minikube service backend-service -n microservices --url

# Ou utiliser port-forward
kubectl port-forward svc/frontend-service 8080:80 -n microservices
kubectl port-forward svc/backend-service 5000:5000 -n microservices
```

## Déploiement sur AWS EKS

### Étape 1: Créer le Cluster EKS

```bash
# Installer eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Créer le cluster
eksctl create cluster \
  --name microservices-cluster \
  --region eu-west-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed
```

### Étape 2: Configurer kubectl

```bash
# Mettre à jour kubeconfig
aws eks update-kubeconfig \
  --name microservices-cluster \
  --region eu-west-1

# Vérifier la connexion
kubectl get nodes
```

### Étape 3: Créer un ECR Repository

```bash
# Créer les repositories
aws ecr create-repository --repository-name backend
aws ecr create-repository --repository-name frontend

# Se connecter à ECR
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.eu-west-1.amazonaws.com
```

### Étape 4: Construire et Pousser les Images

```bash
# Backend
docker build -t backend:latest ./backend
docker tag backend:latest <account-id>.dkr.ecr.eu-west-1.amazonaws.com/backend:latest
docker push <account-id>.dkr.ecr.eu-west-1.amazonaws.com/backend:latest

# Frontend
docker build -t frontend:latest ./frontend
docker tag frontend:latest <account-id>.dkr.ecr.eu-west-1.amazonaws.com/frontend:latest
docker push <account-id>.dkr.ecr.eu-west-1.amazonaws.com/frontend:latest
```

### Étape 5: Déployer avec Helm

```bash
helm install microservices-app ./helm/microservices-app \
  --namespace microservices \
  --create-namespace \
  --set backend.image.repository=<account-id>.dkr.ecr.eu-west-1.amazonaws.com/backend \
  --set frontend.image.repository=<account-id>.dkr.ecr.eu-west-1.amazonaws.com/frontend \
  --set frontend.ingress.host=microservices.yourdomain.com
```

## Configuration CI/CD

### Jenkins

#### Étape 1: Installer Jenkins

```bash
# Sur Kubernetes
helm repo add jenkins https://charts.jenkins.io
helm install jenkins jenkins/jenkins \
  --namespace jenkins \
  --create-namespace \
  --set controller.serviceType=LoadBalancer
```

#### Étape 2: Configurer les Credentials

1. Accéder à Jenkins UI
2. Gérer Jenkins > Credentials
3. Ajouter:
   - Docker Hub credentials
   - Kubernetes kubeconfig
   - GitHub token (si privé)

#### Étape 3: Créer le Pipeline

1. New Item > Pipeline
2. Pipeline from SCM
3. Repository URL: votre repo
4. Script Path: `ci-cd/Jenkinsfile`

### GitLab CI

#### Étape 1: Configurer les Variables

Dans GitLab > Settings > CI/CD > Variables:

```
CI_REGISTRY_USER=<your-registry-user>
CI_REGISTRY_PASSWORD=<your-registry-password>
KUBE_CONFIG=<base64-encoded-kubeconfig>
```

#### Étape 2: Activer les Runners

1. Settings > CI/CD > Runners
2. Enable shared runners ou configure specific runners

#### Étape 3: Push le Code

Le pipeline `.gitlab-ci.yml` se déclenchera automatiquement.

## Monitoring

### Déployer Prometheus et Grafana

```bash
# Créer le namespace
kubectl create namespace monitoring

# Déployer Prometheus
kubectl apply -f monitoring/prometheus/

# Déployer Grafana
kubectl apply -f monitoring/grafana/

# Accéder à Grafana
kubectl port-forward svc/grafana 3000:80 -n monitoring
```

### Accès Grafana

1. URL: http://localhost:3000
2. Login: admin
3. Password: récupérer avec:
   ```bash
   kubectl get secret grafana-secrets -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
   ```

### Importer les Dashboards

1. Grafana > Dashboards > Import
2. Upload `monitoring/grafana/dashboards/microservices-dashboard.json`

## Troubleshooting

### Pods en CrashLoopBackOff

```bash
# Voir les logs
kubectl logs <pod-name> -n microservices

# Décrire le pod
kubectl describe pod <pod-name> -n microservices

# Vérifier les events
kubectl get events -n microservices --sort-by='.lastTimestamp'
```

### Problèmes de Connexion à la Base de Données

```bash
# Vérifier que PostgreSQL est running
kubectl get pods -n microservices -l app=postgres

# Tester la connexion depuis le backend
kubectl exec -it <backend-pod> -n microservices -- \
  curl postgres-service:5432
```

### Images Non Trouvées

```bash
# Pour Minikube, utiliser le daemon Docker de Minikube
eval $(minikube docker-env)

# Reconstruire les images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend
```

### Service Non Accessible

```bash
# Vérifier les services
kubectl get svc -n microservices

# Vérifier les endpoints
kubectl get endpoints -n microservices

# Pour Minikube
minikube service list
```

### Monitoring Non Fonctionnel

```bash
# Vérifier Prometheus
kubectl logs -n monitoring deployment/prometheus

# Vérifier que les métriques sont scrapées
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visiter http://localhost:9090/targets
```

## Commandes Utiles

```bash
# Voir tous les pods
kubectl get pods -A

# Suivre les logs en temps réel
kubectl logs -f deployment/backend -n microservices

# Exécuter une commande dans un pod
kubectl exec -it <pod-name> -n microservices -- /bin/bash

# Redémarrer un déploiement
kubectl rollout restart deployment/backend -n microservices

# Voir l'historique des déploiements
kubectl rollout history deployment/backend -n microservices

# Rollback
kubectl rollout undo deployment/backend -n microservices

# Scaler manuellement
kubectl scale deployment/backend --replicas=5 -n microservices

# Top des ressources
kubectl top nodes
kubectl top pods -n microservices
```

## Support

Pour plus d'informations, consultez:
- [Documentation Kubernetes](https://kubernetes.io/docs/)
- [Documentation Helm](https://helm.sh/docs/)
- [Documentation Docker](https://docs.docker.com/)
