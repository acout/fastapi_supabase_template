#!/usr/bin/env python
"""
Script pour déployer les variables d'environnement du fichier .env.test
vers les secrets GitHub Actions.

Utilisation :
    python scripts/deploy_env_secrets.py

Prérequis :
    - Un token GitHub avec les droits admin:repo_hook, repo
    - Le package python-dotenv
    - Le package PyGithub
    - Un fichier .env.test à la racine du projet
"""

import base64
import os
from pathlib import Path

import dotenv
from github import Github, GithubException

# Configuration
ENV_FILE = ".env.test"
SECRET_SUFFIX = "_TEST"  # Ajouter ce suffixe aux noms des secrets


def load_env_file(env_file):
    """Charger les variables depuis un fichier .env"""
    env_path = Path(env_file)
    if not env_path.exists():
        raise FileNotFoundError(f"Le fichier {env_file} n'existe pas")

    return dotenv.dotenv_values(env_file)


def get_github_token():
    """Obtenir le token GitHub, soit depuis les variables d'environnement,
    soit en demandant à l'utilisateur"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        token = input("Entrez votre token GitHub (avec les droits repo): ")
    return token


def get_repo_info():
    """Obtenir les informations du dépôt, depuis le remote git ou en demandant à l'utilisateur"""
    try:
        import subprocess

        # Essayer d'obtenir l'URL du remote
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Extraire le propriétaire et le nom du dépôt
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]

        if "github.com" in remote_url:
            if remote_url.startswith("https://"):
                parts = remote_url.split("/")
                owner = parts[-2]
                repo = parts[-1]
            elif remote_url.startswith("git@"):
                parts = remote_url.split(":")
                owner_repo = parts[1]
                owner, repo = owner_repo.split("/")
            else:
                raise ValueError(f"Format d'URL non reconnu: {remote_url}")

            return owner, repo
    except (subprocess.SubprocessError, ValueError, IndexError):
        pass

    # Fallback : demander à l'utilisateur
    owner = input("Entrez le nom du propriétaire du dépôt GitHub: ")
    repo = input("Entrez le nom du dépôt GitHub: ")
    return owner, repo


def update_secrets(token, owner, repo_name, env_vars):
    """Mettre à jour les secrets GitHub avec les variables d'environnement"""
    gh = Github(token)
    try:
        repo = gh.get_user(owner).get_repo(repo_name)
    except GithubException as e:
        print(f"Erreur lors de l'accès au dépôt: {e}")
        return False

    success = True
    for key, value in env_vars.items():
        if value:  # Ne pas ajouter de secrets vides
            secret_name = f"{key}{SECRET_SUFFIX}"
            try:
                # Création ou mise à jour du secret
                repo.create_secret(secret_name, value)
                print(f"✅ Secret '{secret_name}' ajouté avec succès")
            except GithubException as e:
                print(f"❌ Erreur lors de l'ajout du secret '{secret_name}': {e}")
                success = False

    return success


def main():
    """Fonction principale du script"""
    print("📝 Déploiement des secrets GitHub depuis le fichier .env.test")

    # Vérifier les prérequis
    try:
        import github
    except ImportError:
        print("❌ Le package PyGithub n'est pas installé. Installez-le avec:")
        print("   pip install PyGithub")
        return

    try:
        import dotenv
    except ImportError:
        print("❌ Le package python-dotenv n'est pas installé. Installez-le avec:")
        print("   pip install python-dotenv")
        return

    # Charger les variables d'environnement
    try:
        env_vars = load_env_file(ENV_FILE)
        print(f"📋 {len(env_vars)} variables trouvées dans {ENV_FILE}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    # Obtenir le token GitHub
    token = get_github_token()
    if not token:
        print("❌ Token GitHub non fourni")
        return

    # Obtenir les informations du dépôt
    owner, repo_name = get_repo_info()
    print(f"🔍 Dépôt cible: {owner}/{repo_name}")

    # Confirmation
    print("\nLes secrets suivants seront créés ou mis à jour:")
    for key in env_vars:
        print(f"  - {key}{SECRET_SUFFIX}")

    confirm = input("\nConfirmer? (o/n): ").lower()
    if confirm != "o" and confirm != "y" and confirm != "yes" and confirm != "oui":
        print("❌ Opération annulée")
        return

    # Mettre à jour les secrets
    success = update_secrets(token, owner, repo_name, env_vars)

    if success:
        print("\n✅ Tous les secrets ont été déployés avec succès!")
        print("\n⚠️  N'oubliez pas d'ajouter CODECOV_TOKEN si vous utilisez Codecov")
    else:
        print("\n⚠️  Certains secrets n'ont pas pu être déployés. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    main()
