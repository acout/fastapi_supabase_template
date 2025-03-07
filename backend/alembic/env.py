from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel
import os
import logging
from dotenv import load_dotenv
from alembic.operations import ops
from app.models.base import RLSModel
from app.models import Base, Item

logger = logging.getLogger("alembic")

from app.core.config import settings

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


def process_revision_directives(context, revision, directives):
    """Ajoute les directives RLS directement dans les opérations"""
    script = directives[0]
    
    if not script.upgrade_ops:
        logger.debug("No upgrade operations found")
        return

    # Collecter les tables créées
    created_tables = []
    for op in script.upgrade_ops.ops:
        if hasattr(op, 'table_name'):
            table_name = op.table_name
            if table_name != 'alembic_version':
                created_tables.append(table_name)
                logger.debug(f"Found table to process: {table_name}")

    # Pour chaque table, ajouter les opérations RLS
    for table_name in created_tables:
        # Trouver le modèle correspondant
        model = None
        for m in [Item]:
            if (getattr(m, '__tablename__', None) == table_name and 
                issubclass(m, RLSModel) and 
                getattr(m, '__rls_enabled__', False)):
                model = m
                break
        
        if model:
            logger.debug(f"Adding RLS for {table_name} from model {model.__name__}")
            
            # Enable RLS
            script.upgrade_ops.ops.append(
                ops.ExecuteSQLOp(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
            )
            
            # Add policies
            for operation, policy in model.get_policies().items():
                sql = f"""
                    CREATE POLICY "{table_name}_{operation}" ON {table_name}
                    FOR {operation.upper()}
                """
                if policy.using:
                    sql += f"\n    USING ({policy.using})"
                if policy.check:
                    sql += f"\n    WITH CHECK ({policy.check})"
                sql += ";"
                
                script.upgrade_ops.ops.append(ops.ExecuteSQLOp(sql))
                logger.debug(f"Added {operation} policy for {table_name}")
            
            # Add downgrade operations at the beginning
            if not script.downgrade_ops:
                script.downgrade_ops = ops.DowngradeOps([])
            
            # Drop policies first
            for operation in model.get_policies().keys():
                script.downgrade_ops.ops.insert(0, 
                    ops.ExecuteSQLOp(
                        f'DROP POLICY IF EXISTS "{table_name}_{operation}" ON {table_name};'
                    )
                )
            
            # Then disable RLS
            script.downgrade_ops.ops.insert(0,
                ops.ExecuteSQLOp(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")
            )


def run_migrations_offline() -> None:
    """Pour générer le SQL sans connexion DB."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        as_sql=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
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
            include_object=include_object,
            process_revision_directives=process_revision_directives
        )

        with context.begin_transaction():
            context.run_migrations()


# Choisir le mode selon l'environnement
if os.getenv("ALEMBIC_OFFLINE_MODE") == "1":
    run_migrations_offline()
else:
    run_migrations_online()
