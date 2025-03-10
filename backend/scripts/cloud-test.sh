#!/bin/bash
set -e

# Ce script lance les tests en utilisant l'instance Supabase cloud

# S'assurer que les variables d'environnement sont chargées
if [ -f "../.env" ]; then
    echo "Chargement des variables d'environnement depuis ../.env"
    set -o allexport
    source ../.env
    set +o allexport
else
    echo "Fichier .env non trouvé. Assurez-vous qu'il existe à la racine du projet."
    exit 1
fi

# Créer ou mettre à jour le fichier .env.test
echo "Création du fichier .env.test pour les tests..."
cat > ../.env.test << EOL
# Configuration pour les tests uniquement
# Utilise la configuration de production pour les tests cloud

# Nom du projet
PROJECT_NAME=FastAPI Supabase Template Test

# Configuration API
API_V1_STR=/api/v1
SECRET_KEY=test_secret_key_for_testing_only
ENVIRONMENT=local

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Supabase
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}

# Base de données
POSTGRES_SERVER=${POSTGRES_SERVER}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_PORT=${POSTGRES_PORT}

# Utilisateur superuser
FIRST_SUPERUSER=${FIRST_SUPERUSER}
FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}
EOL

echo "Fichier .env.test créé avec les paramètres cloud."

# Exécuter les tests
echo "Exécution des tests avec les paramètres cloud..."
python -m pytest tests/ -v

echo "Tests terminés."
