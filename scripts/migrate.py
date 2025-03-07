import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess


def run_migration(environment: str, command: str, message: str = ""):
    """
    Run alembic commands with specific environment
    :param environment: 'development', 'staging', or 'production'
    :param command: 'upgrade', 'downgrade', 'current', etc.
    """
    # Charger le bon fichier d'environnement
    env_file = Path(f".env.{environment}")
    if not env_file.exists():
        print(f"Environment file {env_file} not found!")
        sys.exit(1)

    load_dotenv(env_file)

    # Construire la commande alembic
    if command == "upgrade":
        cmd = ["alembic", "upgrade", "head"]
    elif command == "current":
        cmd = ["alembic", "current"]
    elif command == "revision":
        cmd = ["alembic", "revision", "--autogenerate", "-m", message]
    else:
        cmd = ["alembic"] + command.split()

    # Afficher l'environnement ciblé
    print(f"🎯 Target environment: {environment}")
    print(f"🔌 Database: {os.getenv('POSTGRES_SERVER')}")

    # Exécuter la commande
    try:
        os.chdir("backend")
        subprocess.run(cmd, check=True)
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python migrate.py [environment] [command]")
        print("Environments: development, staging, production")
        print("Commands: upgrade, downgrade, current, revision, etc.")
        sys.exit(1)

    environment = sys.argv[1]
    command = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) > 3 else ""
    run_migration(environment, command, message)
