#!/bin/bash

ENV=${1:-local}  # Par défaut: local

# Charger l'environnement
source .env.$ENV

# Appliquer les migrations via Supabase
supabase db push

echo "Migrations déployées sur l'environnement $ENV" 