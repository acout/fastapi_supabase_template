#!/bin/bash

# Arrêter les conteneurs liés au projet
docker ps -a | grep fastapi_supabase | awk '{print $1}' | xargs -r docker stop

# Supprimer les conteneurs liés au projet
docker ps -a | grep fastapi_supabase | awk '{print $1}' | xargs -r docker rm

# Supprimer les images du devcontainer
docker images | grep vsc-fastapi_supabase | awk '{print $3}' | xargs -r docker rmi -f

# Optionnel : supprimer le volume uv-cache si utilisé
docker volume rm uv-cache

# Optionnel : supprimer tous les volumes non utilisés
docker volume prune -f

# Nettoyer le cache de build
docker builder prune -f
