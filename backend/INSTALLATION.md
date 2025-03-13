# Guide d'installation

Ce document décrit les étapes pour installer et configurer le projet FastAPI Supabase Template.

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template
```

### 2. Nettoyer la structure (après refactorisation)

Afin de s'assurer que la structure du projet est propre et ne contient pas de résidus de l'ancienne structure, exécutez:

```bash
cd backend
bash scripts/cleanup-structure.sh
cd ..
```

### 3. Installer les dépendances

```bash
cd backend
uv sync --all-groups --dev
```

### 4. Configurer les variables d'environnement

Copiez et modifiez le fichier d'exemple pour votre environnement:

```bash
cp .env.example .env
# Éditez le fichier .env avec vos paramètres
```

## Lancement

### Démarrage local

```bash
cd backend
uvicorn app.main:app --reload
```

### Démarrage avec Docker

```bash
docker-compose up -d
```

## Tests

### Tests avec mocks (sans connexion externe)

```bash
cd backend
bash scripts/mock-test.sh
```

### Tests avec Supabase Cloud

```bash
cd backend
bash scripts/cloud-test.sh
```

## Structure du projet

La structure du projet est organisée comme suit:

```
├── backend/           # Tout le code du projet
│   ├── alembic/       # Migrations de base de données
│   ├── app/           # Code source principal
│   │   ├── api/       # Endpoints API
│   │   ├── core/      # Configurations et utilitaires principaux
│   │   ├── crud/      # Opérations CRUD
│   │   ├── models/    # Modèles de données
│   │   ├── schemas/   # Schémas Pydantic
│   │   ├── services/  # Services métier
│   │   ├── utils/     # Utilitaires génériques
│   │   └── main.py    # Point d'entrée de l'application
│   ├── scripts/       # Scripts utilitaires
│   ├── tests/         # Tests
│   ├── .env.test      # Environnement de test
│   └── pyproject.toml # Configuration du projet
├── .pre-commit-config.yaml   # Hooks pre-commit
├── Dockerfile         # Configuration Docker
├── docker-compose.yml # Configuration docker-compose
└── README.md          # Documentation principale
```
