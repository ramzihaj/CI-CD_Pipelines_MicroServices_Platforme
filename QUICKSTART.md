# 🚀 Guide de Démarrage Rapide

Guide pas à pas pour lancer l'application microservices localement.

## ✅ Prérequis

Assurez-vous d'avoir installé :
- **Docker Desktop** (version 24+) - [Télécharger](https://www.docker.com/products/docker-desktop)
- **Git** (pour cloner le projet)

Vérifiez l'installation :
```bash
docker --version
docker-compose --version
```

## 📋 Étapes de Démarrage

### Étape 1 : Naviguer vers le Projet

```bash
cd D:\Project\DevOps\CI-CD_Pipelines
```

### Étape 2 : Nettoyer les Conteneurs Existants (si nécessaire)

Si vous avez déjà essayé de lancer l'application :

```bash
# Arrêter et supprimer tous les conteneurs
docker-compose down -v

# Nettoyer les images (optionnel)
docker system prune -f
```

### Étape 3 : Construire et Démarrer l'Application

```bash
# Construire et démarrer tous les services
docker-compose up -d --build
```

**Explication des options :**
- `-d` : Mode détaché (en arrière-plan)
- `--build` : Forcer la reconstruction des images

### Étape 4 : Vérifier le Statut

```bash
# Voir l'état des conteneurs
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f
```

**Attendez environ 30-60 secondes** que tous les services démarrent complètement.

### Étape 5 : Accéder à l'Application

Une fois tous les services démarrés, ouvrez votre navigateur :

#### 🌐 Frontend (Interface Utilisateur)
```
http://localhost:3000
```
Interface React moderne pour gérer users et produits.

#### 🔧 Backend API
```
http://localhost:5000/api/health
```
Vérifier la santé de l'API.

#### 📊 Grafana (Monitoring)
```
http://localhost:3001
```
- **Username:** admin
- **Password:** admin

#### 📈 Prometheus (Métriques)
```
http://localhost:9090
```

## 🧪 Tester l'Application

### Test Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Créer un utilisateur
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com"}'

# Lister les utilisateurs
curl http://localhost:5000/api/users

# Créer un produit
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":999.99,"stock":10}'

# Lister les produits
curl http://localhost:5000/api/products
```

### Test Frontend

1. Ouvrez http://localhost:3000
2. Cliquez sur **Users** ou **Products**
3. Cliquez sur **+ Add User** ou **+ Add Product**
4. Remplissez le formulaire et créez des entrées

## 📊 Voir les Logs

```bash
# Tous les logs
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend

# Frontend uniquement
docker-compose logs -f frontend

# Base de données
docker-compose logs -f postgres
```

## 🛑 Arrêter l'Application

```bash
# Arrêter les services
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Arrêter et supprimer TOUT (conteneurs + volumes + données)
docker-compose down -v
```

## ⚠️ Dépannage

### Problème : Port déjà utilisé

**Erreur :** `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution :**
```bash
# Windows - Trouver le processus utilisant le port
netstat -ano | findstr :3000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F

# Ou changer le port dans docker-compose.yml
# Modifier "3000:80" en "3001:80" par exemple
```

### Problème : Conteneur en erreur

**Solution :**
```bash
# Voir les logs détaillés
docker-compose logs backend

# Redémarrer un service spécifique
docker-compose restart backend

# Reconstruire complètement
docker-compose down
docker-compose up -d --build
```

### Problème : Base de données vide après redémarrage

C'est normal ! Les données sont dans un volume Docker.

**Pour réinitialiser :**
```bash
docker-compose down -v  # -v supprime les volumes
docker-compose up -d
```

### Problème : Frontend ne se connecte pas au Backend

**Vérifier :**
```bash
# Vérifier que le backend est accessible
curl http://localhost:5000/api/health

# Vérifier les logs du frontend
docker-compose logs frontend

# Redémarrer le frontend
docker-compose restart frontend
```

## 🔍 Commandes Utiles

```bash
# Voir les conteneurs en cours d'exécution
docker ps

# Entrer dans un conteneur (exemple: backend)
docker-compose exec backend bash

# Voir l'utilisation des ressources
docker stats

# Voir les volumes
docker volume ls

# Nettoyer tout Docker
docker system prune -a --volumes
```

## 📁 Structure des Services

```
┌─────────────────┐
│   Frontend      │ ← http://localhost:3000
│   (React)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend       │ ← http://localhost:5000
│   (Flask)       │
└────┬────────┬───┘
     │        │
     ▼        ▼
┌─────────┐ ┌─────────┐
│PostgreSQL│ │  Redis  │
└─────────┘ └─────────┘
```

## 📚 Prochaines Étapes

Après avoir lancé l'application localement :

1. **Explorer l'interface** - Créer des users et produits
2. **Consulter Grafana** - Voir les métriques en temps réel
3. **Tester l'API** - Utiliser curl ou Postman
4. **Lire le code** - Comprendre l'architecture
5. **Déployer sur Kubernetes** - Voir `DEPLOYMENT_GUIDE.md`

## 🆘 Besoin d'Aide ?

### Vérification complète

```bash
# Vérifier que Docker fonctionne
docker run hello-world

# Vérifier les ressources
docker info

# Voir toutes les images
docker images

# Voir tous les conteneurs (même arrêtés)
docker ps -a
```

### Reset complet

Si rien ne fonctionne, reset total :

```bash
# 1. Arrêter tout
docker-compose down -v

# 2. Nettoyer Docker
docker system prune -a --volumes -f

# 3. Redémarrer Docker Desktop

# 4. Relancer
docker-compose up -d --build
```

## ✨ Fonctionnalités de l'Application

- ✅ CRUD complet pour Users et Products
- ✅ Cache Redis pour performances
- ✅ Base de données PostgreSQL persistante
- ✅ Monitoring Prometheus + Grafana
- ✅ Health checks automatiques
- ✅ API RESTful documentée
- ✅ Interface React moderne

---

**Bon déploiement ! 🚀**

Pour un déploiement sur Kubernetes, consultez le fichier `DEPLOYMENT_GUIDE.md`.
