#!/bin/bash

# Ce script permet de lancer les tests avec des mocks Supabase
# Il est utile pour le développement local sans connexion à Supabase

echo "=== Lancement des tests avec mocks Supabase ==="

# Définir les variables d'environnement pour les tests avec mocks
export SKIP_DB_CHECK=true
export MOCK_SUPABASE=true
export SKIP_ENV_CHECK=true

# Lancer les tests
python -m pytest $@

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo "✅ Tous les tests ont passé avec les mocks."
    exit 0
else
    echo "❌ Certains tests ont échoué avec les mocks."
    exit 1
fi
