# 🚀 DevOps Cloud Platform - Application Microservices

Plateforme DevOps complète pour le déploiement automatisé d'une application microservices sur Kubernetes.

## 📋 Architecture

Cette solution comprend :
- **Backend API** (Flask) - Service de gestion des utilisateurs et produits
- **Frontend** (React) - Interface utilisateur moderne
- **Base de données** (PostgreSQL) - Stockage persistant
- **Cache** (Redis) - Amélioration des performances

## 🛠️ Stack Technique

### Application
- **Backend**: Flask (Python 3.11)
- **Frontend**: React 18 avec TypeScript
- **Base de données**: PostgreSQL 15
- **Cache**: Redis 7

### DevOps
- **Conteneurisation**: Docker
- **Orchestration**: Kubernetes (Minikube/EKS)
- **CI/CD**: Jenkins + GitLab CI
- **Gestion des déploiements**: Helm 3
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## 📁 Structure du Projet

```
CI-CD_Pipelines/
├── backend/                    # Service API Flask
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Application React
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── k8s/                       # Manifests Kubernetes
│   ├── namespace.yaml
│   ├── backend/
│   ├── frontend/
│   ├── database/
│   └── monitoring/
├── helm/                      # Helm Charts
│   └── microservices-app/
├── ci-cd/                     # Pipelines CI/CD
│   ├── Jenkinsfile
│   └── .gitlab-ci.yml
├── monitoring/                # Configuration Monitoring
│   ├── prometheus/
│   └── grafana/
└── scripts/                   # Scripts utilitaires
    ├── setup.sh
    └── deploy.sh
```

## 🚀 Démarrage Rapide

### Prérequis

```bash
# Outils nécessaires
- Docker 24+
- Kubernetes (Minikube ou cluster cloud)
- kubectl
- Helm 3
- Jenkins ou GitLab Runner
```

### 1. Configuration Locale avec Minikube

```bash
# Démarrer Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Activer les addons
minikube addons enable ingress
minikube addons enable metrics-server

# Configurer le contexte kubectl
kubectl config use-context minikube
```

### 2. Installation avec Helm

```bash
# Ajouter le namespace
kubectl create namespace microservices

# Installer l'application
helm install my-app ./helm/microservices-app \
  --namespace microservices \
  --create-namespace

# Vérifier le déploiement
kubectl get pods -n microservices
```

### 3. Déploiement Manuel avec kubectl

```bash
# Appliquer tous les manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/database/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Vérifier les services
kubectl get svc -n microservices
```

### 4. Accéder à l'Application

```bash
# Obtenir l'URL Minikube
minikube service frontend-service -n microservices --url

# Ou avec port-forward
kubectl port-forward svc/frontend-service 3000:80 -n microservices
# Accès: http://localhost:3000

kubectl port-forward svc/backend-service 5000:5000 -n microservices
# API: http://localhost:5000/api/health
```

## 🔄 CI/CD Pipeline

### Jenkins Pipeline

Le pipeline automatisé comprend :

1. **Build** - Construction des images Docker
2. **Test** - Tests unitaires et d'intégration
3. **Security Scan** - Analyse de vulnérabilités (Trivy)
4. **Push** - Publication sur Docker Hub/ECR
5. **Deploy** - Déploiement sur Kubernetes
6. **Smoke Tests** - Tests de validation

```bash
# Lancer Jenkins localement
docker run -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

### GitLab CI

Configuration automatique via `.gitlab-ci.yml` avec stages :
- build
- test
- security
- deploy
- monitoring

## 📊 Monitoring & Observabilité

### Prometheus + Grafana

```bash
# Installer Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring --create-namespace

# Installer Grafana
helm install grafana grafana/grafana \
  --namespace monitoring

# Accéder à Grafana
kubectl port-forward svc/grafana 3000:80 -n monitoring
# Login: admin / (voir le secret)
kubectl get secret grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

### Dashboards Disponibles

- **Application Metrics** - Performance des services
- **Kubernetes Cluster** - État du cluster
- **Resource Usage** - CPU, Mémoire, Disque
- **Request Tracing** - Latence et taux d'erreur

## 🧪 Tests

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### Tests d'Intégration

```bash
# Avec l'environnement déployé
./scripts/integration-tests.sh
```

## 🔒 Sécurité

- **Secrets Management**: Kubernetes Secrets / Sealed Secrets
- **Network Policies**: Isolation des services
- **RBAC**: Contrôle d'accès basé sur les rôles
- **Image Scanning**: Trivy pour les vulnérabilités
- **TLS/SSL**: Certificats Let's Encrypt via cert-manager

## 📈 Scalabilité

### Autoscaling Horizontal (HPA)

```bash
# Configurer HPA
kubectl autoscale deployment backend -n microservices \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

### Vertical Pod Autoscaler (VPA)

```bash
# Installer VPA
kubectl apply -f k8s/autoscaling/vpa.yaml
```

## 🌐 Déploiement sur AWS EKS

```bash
# Créer le cluster EKS
eksctl create cluster \
  --name microservices-cluster \
  --region eu-west-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5

# Configurer kubectl
aws eks update-kubeconfig --name microservices-cluster --region eu-west-1

# Déployer l'application
helm install my-app ./helm/microservices-app
```

## 🐛 Dépannage

### Logs des Pods

```bash
# Backend logs
kubectl logs -f deployment/backend -n microservices

# Frontend logs
kubectl logs -f deployment/frontend -n microservices

# Tous les logs d'un namespace
kubectl logs -n microservices --all-containers=true
```

### Debug d'un Pod

```bash
kubectl describe pod <pod-name> -n microservices
kubectl exec -it <pod-name> -n microservices -- /bin/bash
```

## 📚 Documentation Complémentaire

- [Architecture Détaillée](./docs/architecture.md)
- [Guide CI/CD](./docs/ci-cd-guide.md)
- [Monitoring Setup](./docs/monitoring-setup.md)
- [Security Best Practices](./docs/security.md)

## 🎯 Compétences Démontrées

✅ **CI/CD** - Pipelines automatisés Jenkins & GitLab  
✅ **Container Orchestration** - Kubernetes & Helm  
✅ **Infrastructure as Code** - Manifests YAML déclaratifs  
✅ **Monitoring** - Prometheus, Grafana, métriques applicatives  
✅ **Automatisation** - Scripts de déploiement et tests  
✅ **Sécurité** - Network policies, secrets, scanning  
✅ **Scalabilité** - HPA, VPA, résilience  

## 👨‍💻 Auteur

Plateforme DevOps Cloud - Microservices Application

## 📄 Licence

MIT License
