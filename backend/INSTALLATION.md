# Guide d'installation

Ce document décrit les étapes pour installer et configurer le projet FastAPI Supabase Template.

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template
```

### 2. Installer les dépendances

```bash
cd backend
uv sync --all-groups --dev
```

### 3. Configurer les variables d'environnement

Copiez et modifiez le fichier d'exemple pour votre environnement:

```bash
cp .env.example .env
# Éditez le fichier .env avec vos paramètres
```

Pour les tests, créez un fichier `.env.test` adapté à votre environnement de test ou copiez simplement le fichier `.env`:

```bash
cp .env .env.test
# Modifiez si nécessaire pour votre environnement de test
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

### Tests avec l'instance Supabase cloud

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
│   └── pyproject.toml # Configuration du projet
├── .pre-commit-config.yaml   # Hooks pre-commit
├── Dockerfile         # Configuration Docker
├── docker-compose.yml # Configuration docker-compose
└── README.md          # Documentation principale
```

## Intégration Supabase

Le projet utilise Supabase pour:

1. **Authentification** - via Supabase Auth
2. **Base de données** - via PostgreSQL hosté sur Supabase
3. **Stockage** - via les buckets Supabase Storage

Pour configurer l'accès à votre projet Supabase, modifiez les variables suivantes dans le fichier `.env`:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsIn...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsIn...

# PostgreSQL connection
POSTGRES_SERVER=your-project-db.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=postgres
```