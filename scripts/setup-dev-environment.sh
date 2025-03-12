#!/bin/bash

# Ce script installe et configure l'environnement de développement
# Il doit être exécuté depuis la racine du projet

set -e

echo "Installation de l'environnement de développement..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Installer pre-commit si nécessaire
if ! command -v pre-commit &> /dev/null; then
    echo "Installation de pre-commit..."
    pip install pre-commit
fi

# Installer les hooks pre-commit
echo "Installation des hooks pre-commit..."
pre-commit install

# Vérifier si uv est installé et l'installer si nécessaire
if ! command -v uv &> /dev/null; then
    echo "Installation de uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Actualiser le PATH pour inclure uv
    source ~/.bashrc || source ~/.bash_profile || true
fi

# Installer les dépendances du projet
echo "Installation des dépendances du projet..."
cd backend
uv sync --all-groups --dev
cd ..

echo "L'environnement de développement a été configuré avec succès!"
echo "Vous pouvez maintenant développer avec les outils suivants:"
echo " - pre-commit: pour vérifier automatiquement la qualité du code avant chaque commit"
echo " - uv: pour gérer les dépendances Python"
echo " - tests: exécutez 'cd backend && pytest' pour lancer les tests"
