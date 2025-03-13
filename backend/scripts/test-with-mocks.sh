#!/bin/bash
# Ce script lance les tests en utilisant des mocks pour Supabase
# et en ignorant les vérifications de connexion à la base de données

echo "Exécution des tests avec mocks..."

export MOCK_SUPABASE=true
export SKIP_DB_CHECK=true
export SKIP_ENV_CHECK=true

python -m pytest "$@"
