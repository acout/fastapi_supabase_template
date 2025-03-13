import os
from pathlib import Path
from dotenv import load_dotenv

# Charger .env.test AVANT tout autre import
test_env_path = Path(__file__).parent.parent.parent / ".env.test"
if not test_env_path.exists():
    # Si .env.test n'existe pas, essayer de charger .env standard
    test_env_path = Path(__file__).parent.parent.parent / ".env"
    if not test_env_path.exists():
        raise FileNotFoundError(
            f"Neither .env.test nor .env file found at {test_env_path.parent}. "
            "Please create one with the required environment variables."
        )

print(f"Loading test environment from: {test_env_path}")
load_dotenv(test_env_path)

# Vérifier les variables requises
required_vars = [
    "PROJECT_NAME",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "POSTGRES_SERVER",
    "POSTGRES_USER",
    "FIRST_SUPERUSER",
    "FIRST_SUPERUSER_PASSWORD"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables in {test_env_path.name}: {', '.join(missing_vars)}"
    )

# Maintenant on peut importer le reste
import uuid
from collections.abc import Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from gotrue import User
from sqlmodel import Session, delete
from supabase import Client, create_client
from supabase._async.client import AsyncClient, create_client as create_async_client
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models.item import Item, ItemCreate
from app.schemas.auth import Token

from app import crud

# Configuration de Faker
fake = Faker()

@pytest.fixture(scope="module")
def db() -> Generator[Session, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.exec(statement)  # type: ignore
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def global_cleanup() -> Generator[None, None]:
    yield
    # Nettoyage uniquement des utilisateurs de test, pas du superuser
    super_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    users = super_client.auth.admin.list_users()
    for user in users:
        if user.email != settings.FIRST_SUPERUSER:  # Ne pas supprimer le superuser
            super_client.auth.admin.delete_user(user.id)


@pytest.fixture(scope="function")
def super_client() -> Generator[Client, None]:
    super_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    yield super_client


@pytest.fixture(scope="session")
def supabase():
    """Client Supabase de base avec la clé anon"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )


@pytest.fixture(scope="session")
def superuser_auth() -> dict:
    """Obtient un jeton d'authentification pour le superuser"""
    supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # Essayer de se connecter avec le superuser
    try:
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD
        })
        token = auth_response.session.access_token
    except Exception as e:
        print(f"Erreur lors de la connexion avec le superuser: {e}")
        # Essayer de créer le superuser s'il n'existe pas
        try:
            auth_response = supabase_client.auth.sign_up({
                "email": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD
            })
            token = auth_response.session.access_token
        except Exception as signup_error:
            print(f"Erreur lors de la création du superuser: {signup_error}")
            raise
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
async def async_supabase_client() -> AsyncClient:
    """Client Supabase asynchrone pour les tests"""
    return await create_async_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )


@pytest.fixture(scope="session")
async def async_superuser_client() -> AsyncClient:
    """Client Supabase asynchrone authentifié en tant que superuser"""
    client = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    # Se connecter avec le superuser
    try:
        auth_response = await client.auth.sign_in_with_password({
            "email": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD
        })
    except Exception as e:
        print(f"Erreur lors de la connexion asynchrone avec le superuser: {e}")
        # Tenter de créer le superuser
        auth_response = await client.auth.sign_up({
            "email": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD
        })
    
    return client


@pytest.fixture
async def test_user(supabase):
    """Crée un utilisateur de test"""
    user_data = {
        "email": fake.email(),
        "password": fake.password(length=12)
    }
    
    user = await supabase.auth.sign_up(user_data)
    
    yield user
    
    # Cleanup: supprimer l'utilisateur et ses données
    await supabase.table("profiles").delete().eq("user_id", user.user.id).execute()


@pytest.fixture
async def test_users(supabase):
    """Crée deux utilisateurs de test avec leurs clients"""
    users = []
    clients = []
    
    for _ in range(2):
        user_data = {
            "email": fake.email(),
            "password": fake.password(length=12)
        }
        user = await supabase.auth.sign_up(user_data)
        users.append(user)
        
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            headers={"Authorization": f"Bearer {user.session.access_token}"}
        )
        clients.append(client)
    
    yield {
        "users": users,
        "clients": clients
    }
    
    # Cleanup
    for user in users:
        await supabase.table("profiles").delete().eq("user_id", user.user.id).execute()


@pytest.fixture(scope="function")
def test_item(db: Session, test_user: User) -> Generator[Item, None]:
    item_in = ItemCreate(
        title=fake.sentence(nb_words=3), description=fake.text(max_nb_chars=200)
    )
    yield crud.item.create(db, owner_id=uuid.UUID(test_user.user.id), obj_in=item_in)


@pytest.fixture(scope="function")
def token(super_client: Client) -> Generator[Token, None]:
    response = super_client.auth.sign_up(
        {"email": fake.email(), "password": "testpassword123"}
    )
    yield Token(access_token=response.session.access_token)
