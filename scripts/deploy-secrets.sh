#!/bin/bash

# Script de raccourci pour déployer les secrets vers GitHub
# Utilisé dans le devcontainer pour simplifier le processus

set -e  # Exit on error

# Couleurs pour les messages
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}🔐 Outil de déploiement des secrets GitHub${NC}"
echo

# Vérifier le fichier .env.test
if [ ! -f ".env.test" ]; then
    echo -e "${RED}❌ Fichier .env.test non trouvé à la racine du projet${NC}"
    exit 1
fi

# Vérifier l'authentification GitHub
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}⚠️ Vous n'êtes pas connecté à GitHub CLI${NC}"
    echo -e "${BLUE}ℹ️ Authentification avec GitHub CLI...${NC}"
    gh auth login
fi

# Demander confirmation
echo -e "${YELLOW}⚠️ Cette opération va créer des secrets GitHub à partir de votre fichier .env.test${NC}"
echo -e "${YELLOW}⚠️ Les secrets existants avec les mêmes noms seront écrasés${NC}"
echo
read -p "Continuer? (o/n): " confirm
if [[ ! "$confirm" =~ ^[oOyY]$ ]]; then
    echo -e "${YELLOW}ℹ️ Opération annulée${NC}"
    exit 0
fi

# Exécuter le script Python
echo -e "${BLUE}ℹ️ Déploiement des secrets...${NC}"
echo

# Obtenir le token GitHub via GitHub CLI
token=$(gh auth token)
export GITHUB_TOKEN="$token"

# Exécuter le script de déploiement
python ./scripts/deploy_env_secrets.py

echo
echo -e "${GREEN}✅ Opération terminée${NC}"
