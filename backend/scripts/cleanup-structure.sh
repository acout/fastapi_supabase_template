#!/bin/bash

# Ce script nettoie les dossiers obsoletes apres la refactorisation

echo "=== Nettoyage de la structure du projet ==="

# Supprimer les dossiers obsoletes
if [ -d "../app" ]; then
    echo "Suppression du dossier app obsolete..."
    rm -rf ../app
fi

if [ -d "../supabase" ]; then
    echo "Suppression du dossier supabase obsolete..."
    rm -rf ../supabase
fi

# Verifier que les dossiers ont bien ete supprimes
if [ ! -d "../app" ] && [ ! -d "../supabase" ]; then
    echo "Structure nettoyee avec succes."
else
    echo "Probleme lors du nettoyage de la structure."
    exit 1
fi
