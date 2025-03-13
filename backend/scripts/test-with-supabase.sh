#!/bin/bash
# Ce script lance les tests en utilisant une connexion réelle à Supabase

echo "Exécution des tests avec connexion Supabase réelle..."

export MOCK_SUPABASE=false
export SKIP_DB_CHECK=false
export SKIP_ENV_CHECK=false

python -m pytest "$@"
