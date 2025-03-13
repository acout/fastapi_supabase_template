# FastAPI Supabase Template

Un template de projet FastAPI intégrant Supabase pour l'authentification, la base de données et le stockage de fichiers.

## Fonctionnalités

- **Authentification** avec Supabase Auth
- **Base de données** PostgreSQL via SQLModel et Supabase
- **Row Level Security (RLS)** pour la protection des données
- **Stockage de fichiers** avec Supabase Storage et policies RLS
- **Upload de fichiers** avec métadonnées en base de données
- **API RESTful** complète avec FastAPI
- **Documentation automatique** avec Swagger UI
- **Tests** avec l'instance Supabase cloud

## Structure du projet

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

## Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template

# Installer les dépendances
cd backend
uv sync --all-groups --dev

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres Supabase
```

Pour plus de détails, consultez [le guide d'installation](backend/INSTALLATION.md).

## Utilisation de l'API de stockage

L'API de stockage permet de gérer des fichiers avec Supabase Storage.

### Upload de fichiers

```bash
# Upload d'une image de profil
curl -X POST "http://localhost:8000/api/v1/storage/upload/profile-picture" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "description=Ma photo de profil"

# Upload d'un document lié à un item
curl -X POST "http://localhost:8000/api/v1/storage/upload/document/ITEM_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Documentation importante"
```

### Récupération des métadonnées

```bash
# Liste des fichiers de l'utilisateur
curl -X GET "http://localhost:8000/api/v1/storage/files" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Obtenir les métadonnées d'un fichier spécifique
curl -X GET "http://localhost:8000/api/v1/storage/file/FILE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Téléchargement de fichiers

```bash
# Obtenir une URL de téléchargement signée
curl -X GET "http://localhost:8000/api/v1/storage/file/FILE_ID/url" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Tests

### Tests avec Supabase Cloud

```bash
cd backend
bash scripts/cloud-test.sh
```

## Lancement de l'application

### Démarrage local

```bash
cd backend
uvicorn app.main:app --reload
```

### Démarrage avec Docker

```bash
docker-compose up -d
```

L'application est accessible à l'adresse http://localhost:8000 et la documentation Swagger à http://localhost:8000/docs

## Docker

Construction de l'image :

```bash
docker build -t acout/fastapi_supabase_template .
```

Exécution de l'image :

```bash
docker run --network host \
  --env-file .env \
  -it acout/fastapi_supabase_template:latest
```
