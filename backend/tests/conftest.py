import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.utils.testing import MockSupabaseClient, should_mock_supabase, should_skip_db_check, should_skip_env_check

# Configuration pour utiliser SQLite en mémoire pour les tests
@pytest.fixture(name="engine")
def engine_fixture():
    """Crée un moteur SQLite en mémoire pour les tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    """Crée une session de base de données pour les tests."""
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture():
    """Crée un client de test pour l'API."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(name="supabase_client")
def supabase_client_fixture():
    """Retourne un client Supabase réel ou mock selon les variables d'environnement."""
    if should_mock_supabase():
        return MockSupabaseClient()
    else:
        try:
            from supabase import create_client
            # Ignorez la vérification des variables d'environnement si demandé
            if should_skip_env_check():
                supabase_url = os.environ.get("SUPABASE_URL", "http://localhost:8000")
                supabase_key = os.environ.get("SUPABASE_KEY", "mock-key")
            else:
                supabase_url = settings.SUPABASE_URL
                supabase_key = settings.SUPABASE_KEY
                
            if not should_skip_db_check():
                return create_client(supabase_url, supabase_key)
            else:
                return MockSupabaseClient()
        except Exception as e:
            # En cas d'erreur, utiliser le mock si SKIP_DB_CHECK est activé
            if should_skip_db_check():
                return MockSupabaseClient()
            raise e
