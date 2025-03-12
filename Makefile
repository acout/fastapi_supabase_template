# Makefile pour faciliter les opérations courantes

.PHONY: help install dev test lint format deploy-secrets

help: ## Affiche l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe les dépendances du projet
	pip install -e ./backend
	pip install pre-commit python-dotenv PyGithub
	pre-commit install

dev: ## Démarre le serveur de développement
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Exécute les tests
	cd backend && pytest

lint: ## Vérifie la qualité du code
	pre-commit run --all-files

format: ## Formate le code
	cd backend && ruff format .

deploy-secrets: ## Déploie les secrets du fichier .env.test vers GitHub
	chmod +x ./scripts/deploy-secrets.sh
	./scripts/deploy-secrets.sh
