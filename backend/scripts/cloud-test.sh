#!/bin/bash
set -e

# Ce script lance les tests en utilisant l'instance Supabase cloud

# Chemin du fichier .env (à la racine du projet)
ENV_FILE="../.env"
ENV_TEST_FILE="../.env.test"
ENV_TEST_BACKUP="../.env.test.backup"

# S'assurer que les variables d'environnement sont chargées
if [ -f "$ENV_FILE" ]; then
    echo "Chargement des variables d'environnement depuis $ENV_FILE"
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
else
    echo "Fichier .env non trouvé à $ENV_FILE. Assurez-vous qu'il existe à la racine du projet."
    exit 1
fi

# Vérifier les variables requises
if [ -z "${SUPABASE_SERVICE_KEY}" ]; then
    echo "AVERTISSEMENT: La variable SUPABASE_SERVICE_KEY n'est pas définie dans votre fichier .env"
    echo "Cette variable est nécessaire pour les tests"
    
    # Utiliser la même valeur que SUPABASE_KEY si celle-ci est définie
    if [ -n "${SUPABASE_KEY}" ]; then
        echo "Utilisation de la valeur de SUPABASE_KEY comme valeur pour SUPABASE_SERVICE_KEY"
        export SUPABASE_SERVICE_KEY="${SUPABASE_KEY}"
        echo "Note: Pour Supabase Cloud, SUPABASE_SERVICE_KEY doit être votre service_role key (pas l'anon key)"
    else
        echo "Veuillez entrer votre clé service_role Supabase:"
        read -r SUPABASE_SERVICE_KEY
        export SUPABASE_SERVICE_KEY
    fi
fi

# Vérifier les autres variables essentielles
REQUIRED_VARS=("SUPABASE_URL" "SUPABASE_KEY" "POSTGRES_SERVER" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "FIRST_SUPERUSER" "FIRST_SUPERUSER_PASSWORD")
MISSING_VARS=false

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "ERREUR: La variable ${VAR} n'est pas définie dans votre fichier .env"
        MISSING_VARS=true
    fi
done

if [ "$MISSING_VARS" = true ]; then
    echo "Il manque des variables d'environnement requises. Veuillez compléter votre fichier .env"
    exit 1
fi

# Afficher les informations de connexion pour débogage
echo ""
echo "Configuration utilisée pour les tests:"
echo "SUPABASE_URL: ${SUPABASE_URL}"
echo "POSTGRES_SERVER: ${POSTGRES_SERVER}"
echo "POSTGRES_USER: ${POSTGRES_USER}"
echo "POSTGRES_DB: ${POSTGRES_DB}"
echo "FIRST_SUPERUSER: ${FIRST_SUPERUSER}"
echo ""

# Sauvegarder le fichier .env.test existant s'il existe
if [ -f "$ENV_TEST_FILE" ]; then
    echo "Sauvegarde du fichier .env.test existant..."
    cp "$ENV_TEST_FILE" "$ENV_TEST_BACKUP"
    echo "Fichier sauvegardé dans $ENV_TEST_BACKUP"
fi

# Créer un fichier .env.test temporaire pour les tests
echo "Création d'un fichier .env.test temporaire pour les tests..."
cat > "$ENV_TEST_FILE" << EOL
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
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Utilisateur superuser
FIRST_SUPERUSER=${FIRST_SUPERUSER}
FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}
EOL

echo "Fichier .env.test temporaire créé."

# Exécuter les tests
echo "Exécution des tests avec les paramètres cloud..."
python -m pytest tests/ -v
TEST_EXIT_CODE=$?

# Restaurer le fichier .env.test original si la sauvegarde existe
if [ -f "$ENV_TEST_BACKUP" ]; then
    echo "Restauration du fichier .env.test original..."
    mv "$ENV_TEST_BACKUP" "$ENV_TEST_FILE"
    echo "Fichier .env.test restauré."
fi

echo "Tests terminés."
exit $TEST_EXIT_CODE
