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

## Structure du projet

```
├── app                  # Application principale
│   ├── api              # Routes de l'API
│   ├── core             # Configuration et fonctionnalités de base
│   ├── crud             # Opérations CRUD pour la base de données
│   ├── models           # Modèles de données SQLModel
│   ├── schemas          # Schémas Pydantic
│   ├── services         # Services d'application
│   └── utils            # Utilitaires
├── tests                # Tests unitaires et d'intégration
├── alembic              # Migrations de base de données
└── supabase             # Configuration Supabase
```

## Environnement

### Python

> [uv](https://github.com/astral-sh/uv) est un gestionnaire de paquets Python ultra-rapide, écrit en Rust.

```bash
cd backend
uv sync --all-groups --dev
```

### [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

Installation de supabase-cli

```bash
# brew sur Linux https://brew.sh/
brew install supabase/tap/supabase
```

Lancement des conteneurs Docker Supabase

```bash
# à la racine du dépôt
supabase start
```

> [!NOTE]
>```bash
># Mise à jour du fichier `.env`
>bash scripts/update-env.sh
>```
> Modifiez le fichier `.env` à partir de la sortie de `supabase start` ou exécutez `supabase status` manuellement.

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

```bash
cd backend
# Test de connexion à la base de données et migration
scripts/pre-start.sh
# Tests unitaires
scripts/test.sh
# Test de connexion à la base de données et code de test
scripts/tests-start.sh
```

## Docker

> [!note]
> `acout/fastapi_supabase_template` est le nom de votre image Docker, remplacez-le par le vôtre

Construction de l'image

```bash
cd backend
docker build -t acout/fastapi_supabase_template .
```

Test de l'image

```bash
bash scripts/update-env.sh
supabase start
cd backend
docker run --network host \
  --env-file ../.env \
  -it acout/fastapi_supabase_template:latest \
  bash -c "sh scripts/pre-start.sh && sh scripts/tests-start.sh"
```
