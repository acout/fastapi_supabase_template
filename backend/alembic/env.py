from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.models import Base, Item  # vos modèles SQLModel

# Charger les variables d'environnement
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support


target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Retourne l'URL de connexion pour le session pooler Supabase"""
    project_id = os.getenv("SUPABASE_PROJECT_ID")
    password = os.getenv("POSTGRES_PASSWORD")
    server = os.getenv("POSTGRES_SERVER", "aws-0-eu-west-3.pooler.supabase.com")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "postgres")
    user = os.getenv("POSTGRES_USER", "postgres")
    
    # Construction du username spécial pour le pooler
    pooler_user = f"{user}.{project_id}" if project_id else user
    
    return f"postgresql://{pooler_user}:{password}@{server}:{port}/{db}"


def include_object(object, name, type_, reflected, compare_to):
    # Ignorer la table users du schéma auth
    if type_ == "table" and name == "users" and object.schema == "auth":
        return False
    return True


def run_migrations_offline() -> None:
    """Pour générer le SQL sans connexion DB."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        as_sql=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Pour appliquer les migrations avec connexion DB."""
    from sqlalchemy import engine_from_config, pool

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


# Choisir le mode selon l'environnement
if os.getenv("ALEMBIC_OFFLINE_MODE") == "1":
    run_migrations_offline()
else:
    run_migrations_online()
