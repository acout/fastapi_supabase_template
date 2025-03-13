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
- **Tests unitaires** complets
- **Infrastructure simplifiée** pour une maintenance facilitée

## Structure du projet

```
/
|-- .github/           # GitHub Actions et configurations
|-- backend/           # Tout le code du projet
|   |-- alembic/       # Migrations de base de données
|   |-- app/           # Code source principal
|   |   |-- api/       # Endpoints API
|   |   |-- core/      # Configurations et utilitaires principaux
|   |   |-- crud/      # Opérations CRUD
|   |   |-- models/    # Modèles de données
|   |   |-- schemas/   # Schémas Pydantic
|   |   |-- services/  # Services métier
|   |   |-- utils/     # Utilitaires génériques
|   |   |-- main.py    # Point d'entrée de l'application
|   |-- scripts/       # Scripts utilitaires
|   |-- tests/         # Tests
|   |-- .env           # Environnement de développement
|   |-- .env.test      # Environnement de test
|   |-- pyproject.toml # Configuration du projet
|-- .pre-commit-config.yaml   # Hooks pre-commit
|-- Dockerfile         # Configuration Docker
|-- docker-compose.yml # Configuration docker-compose
```

## Environnement

### Python

> [uv](https://github.com/astral-sh/uv) est un gestionnaire de paquets Python ultra-rapide, écrit en Rust.

```bash
cd backend
uv sync --all-groups --dev
```

## Utilisation de l'API de stockage

L'API de stockage permet de gérer des fichiers avec Supabase Storage. Voici les principales fonctionnalités :

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

### Tests avec mocks (sans dépendances externes)

```bash
cd backend
# Exécuter les tests unitaires avec des mocks
MOCK_SUPABASE=true SKIP_DB_CHECK=true pytest tests/
```

### Tests avec Supabase Cloud

Pour tester avec votre instance Supabase cloud, assurez-vous d'avoir configuré votre fichier `.env` avec les informations de connexion à votre Supabase cloud, puis exécutez :

```bash
cd backend
# Exécuter les tests avec l'instance Supabase cloud
bash scripts/test.sh
```

## Lancement de l'application

### Avec Docker

```bash
# Construction et lancement des conteneurs
docker-compose up --build
```

### En développement local

```bash
cd backend
uvicorn app.main:app --reload
```

L'application est ensuite accessible à l'adresse http://localhost:8000 et la documentation Swagger à http://localhost:8000/docs

## Docker

> [!note]
> `acout/fastapi_supabase_template` est le nom de votre image Docker, remplacez-le par le vôtre

Construction de l'image

```bash
docker build -t acout/fastapi_supabase_template .
```

Test de l'image

```bash
cd backend
docker run --env-file .env \
  -it acout/fastapi_supabase_template:latest \
  bash -c "sh scripts/tests-start.sh"
```
