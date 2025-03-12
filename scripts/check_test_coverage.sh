#!/bin/bash

# Script pour vérifier la couverture de code pour les fichiers modifiés

set -e

# Répertoire du projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
cd "$PROJECT_DIR"

# Obtenir la liste des fichiers Python modifiés (non committés ou différents de main)
MODIFIED_FILES=$(git diff --name-only main... | grep -E '\.py$' | grep -v 'test_' | grep -v 'conftest.py' | grep -v 'setup.py' || true)

if [ -z "$MODIFIED_FILES" ]; then
    echo "Aucun fichier Python modifié détecté."
    exit 0
fi

echo "Vérification de la couverture de tests pour les fichiers modifiés :"
echo "$MODIFIED_FILES"

# Exécuter pytest avec coverage sur les fichiers modifiés
cd backend
python -m pytest --cov=app $(echo "$MODIFIED_FILES" | sed 's/backend\///g' | tr '\n' ' ') -v

# Obtenir le rapport de couverture
echo "\nRapport de couverture détaillé :"
python -m pytest --cov=app --cov-report term-missing $(echo "$MODIFIED_FILES" | sed 's/backend\///g' | tr '\n' ' ')

# Vérifier si la couverture globale est d'au moins 80%
COVERAGE=$(python -m pytest --cov=app $(echo "$MODIFIED_FILES" | sed 's/backend\///g' | tr '\n' ' ') --cov-report=term-missing | grep 'TOTAL' | awk '{print $NF}' | sed 's/%//')

if (( $(echo "$COVERAGE < 80" | bc -l) )); then
    echo "\nERREUR: La couverture de test est de $COVERAGE%, ce qui est inférieur au minimum requis de 80%."
    exit 1
else
    echo "\nSUCCÈS: La couverture de test est de $COVERAGE%, ce qui est supérieur ou égal au minimum requis de 80%."
fi
