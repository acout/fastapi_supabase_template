import os
import sys
from dotenv import load_dotenv
import subprocess


def generate_migration(message: str):
    # Setup environnement
    env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(env_path)

    # Assurer que le dossier versions existe
    os.makedirs("backend/alembic/versions", exist_ok=True)

    # Préparer l'environnement pour Alembic
    env_vars = {
        "PYTHONPATH": "/app",
        "POSTGRES_SERVER": os.getenv("POSTGRES_SERVER"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }

    # Se placer dans le bon dossier
    os.chdir("backend")
    current_env = os.environ.copy()
    current_env.update(env_vars)

    # 1. Générer la nouvelle révision
    print("Generating new revision...")
    cmd = f"alembic revision --autogenerate -m '{message}'"
    result = subprocess.run(cmd.split(), env=current_env)
    if result.returncode != 0:
        print("Erreur lors de la génération de la révision")
        return

    # 2. Appliquer la migration
    print("Applying migration to database...")
    cmd = "alembic upgrade head"
    result = subprocess.run(cmd.split(), env=current_env)
    if result.returncode == 0:
        print("Migration appliquée avec succès !")
    else:
        print("Erreur lors de l'application de la migration")


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "migration"
    generate_migration(message)
