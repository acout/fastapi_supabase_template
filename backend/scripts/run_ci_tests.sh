#!/bin/bash
# Script pour exécuter les tests en mode CI, en simulant l'environnement CI/CD

set -e

# S'assurer qu'on est dans le bon répertoire
if [ ! -d "backend" ] && [ ! -d "../backend" ]; then
    echo "Erreur: Le script doit être exécuté depuis le répertoire racine ou backend du projet"
    exit 1
fi

# Aller au répertoire backend si on est dans la racine
if [ -d "backend" ]; then
    cd backend
fi

# Installer pytest-asyncio s'il n'est pas déjà installé
python -m pip install pytest-asyncio httpx python-dotenv

# Exécuter les tests avec les paramètres appropriés
echo "===== Exécution des tests en mode CI ====="
echo "Note: Ceci simule l'environnement CI/CD pour les tests"

# Exécuter pytest avec le mode verbeux et génération du rapport de couverture
pytest -v --cov=app --cov-report=term
