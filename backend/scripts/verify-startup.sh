#!/bin/bash

# Ce script vérifie que l'application démarre correctement avec les variables d'environnement de test

echo "=== Vérification du démarrage de l'application ==="

# Définir les variables d'environnement pour le test
export SKIP_DB_CHECK=true
export MOCK_SUPABASE=true
export SKIP_ENV_CHECK=true

# Démarrer l'application en arrière-plan
uvicorn app.main:app --host 0.0.0.0 --port 8088 &
PID=$!

# Attendre que l'application démarre
sleep 3

# Vérifier que l'application répond
echo "Test de connexion à l'API..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8088/)

# Arrêter l'application
kill $PID
wait $PID 2>/dev/null

# Vérifier le résultat
if [ "$RESPONSE" = "200" ]; then
    echo "✅ L'application a démarré avec succès (code: $RESPONSE)."
    exit 0
else
    echo "❌ L'application n'a pas démarré correctement (code: $RESPONSE)."
    exit 1
fi
