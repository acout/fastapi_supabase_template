import io
import uuid
from typing import Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.auth import get_current_user, get_super_client
from app.core.config import settings
from app.main import app
from app.models.file import FileMetadata
from app.models.storage import ItemDocuments, ProfilePictures
from app.schemas.auth import UserIn

# Créer un moteur de base de données en mémoire pour les tests
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_db() -> Generator[Session, None, None]:
    """Générateur de session de base de données pour les tests"""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


async def get_test_superuser() -> UserIn:
    """Utilisateur superuser pour les tests d'authentification"""
    return UserIn(
        id="11111111-1111-1111-1111-111111111111",  # ID fictif mais constant
        email=settings.FIRST_SUPERUSER,
        access_token="test_superuser_token",
    )


# Mock pour le service de stockage Supabase
class MockStorageService:
    async def upload_file(self, *args, **kwargs):
        # Simuler un chemin de fichier et des métadonnées
        path = f"test/{uuid.uuid4()}/test.txt"
        
        # Si session est fourni, créer un objet FileMetadata
        session = kwargs.get("session")
        if session:
            file_meta = FileMetadata(
                id=uuid.uuid4(),
                owner_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),  # ID du superuser
                filename=kwargs.get("file").filename or "test.txt",
                content_type=kwargs.get("file").content_type or "text/plain",
                size=100,
                bucket_name=kwargs.get("bucket_class").name,
                path=path,
                description=kwargs.get("description"),
                item_id=kwargs.get("record_id")
            )
            session.add(file_meta)
            session.commit()
            session.refresh(file_meta)
            return path, file_meta
        return path, None

    async def get_file_url(self, bucket_name, file_path, expiration=60):
        return f"https://example.com/{bucket_name}/{file_path}?expires={expiration}"

    async def download_file(self, bucket_name, file_path):
        return io.BytesIO(b"test content")

    async def delete_file(self, bucket_name, file_path, session=None, metadata_id=None):
        if session and metadata_id:
            metadata = session.get(FileMetadata, metadata_id)
            if metadata:
                session.delete(metadata)
                session.commit()
        return True

    async def list_files(self, bucket_name, path=""):
        return [
            {"name": "test1.txt", "id": "123", "metadata": {}},
            {"name": "test2.txt", "id": "456", "metadata": {}}
        ]

    async def initialize_buckets(self, buckets):
        return True


async def get_test_storage_service():
    return MockStorageService()


# Mock pour le client Supabase
async def get_test_super_client():
    mock_client = AsyncMock()
    mock_client.auth.get_user.return_value = {
        "user": {
            "id": "11111111-1111-1111-1111-111111111111",
            "email": settings.FIRST_SUPERUSER
        }
    }
    return mock_client


@pytest.fixture
def client(superuser_auth):
    """Client de test avec authentification superuser"""
    # Remplacer les dépendances
    app.dependency_overrides[get_current_user] = get_test_superuser
    app.dependency_overrides[get_super_client] = get_test_super_client
    app.dependency_overrides["get_db"] = get_test_db
    
    # Remplacer le service de stockage par notre mock
    from app.api.deps import get_storage_service_dep
    app.dependency_overrides[get_storage_service_dep] = get_test_storage_service
    
    with TestClient(app) as c:
        # Ajouter l'en-tête d'authentification du superuser
        c.headers.update(superuser_auth)
        yield c

    # Nettoyer les remplacements après les tests
    app.dependency_overrides = {}


@pytest.fixture
def test_db():
    """Base de données SQLite en mémoire pour les tests"""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def superuser_id():
    """ID du superuser pour les tests"""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


def test_upload_profile_picture(client):
    """Test pour l'upload d'une image de profil"""
    # Créer un fichier de test
    file_content = b"test image content"
    file = {"file": ("test.jpg", file_content, "image/jpeg")}
    form_data = {"description": "Test profile picture"}
    
    # Appeler l'endpoint
    response = client.post(
        "/api/v1/storage/upload/profile-picture",
        files=file,
        data=form_data
    )
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.jpg"
    assert data["content_type"] == "image/jpeg"
    assert data["bucket_name"] == ProfilePictures.name
    assert data["description"] == "Test profile picture"


def test_upload_item_document(client, test_db, superuser_id):
    """Test pour l'upload d'un document lié à un item"""
    # Créer un item de test dans la base de données
    from app.models.item import Item
    item = Item(
        id=uuid.uuid4(),
        title="Test item",
        owner_id=superuser_id
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    # Créer un fichier de test
    file_content = b"test document content"
    file = {"file": ("test.pdf", file_content, "application/pdf")}
    form_data = {"description": "Test document"}
    
    # Appeler l'endpoint
    response = client.post(
        f"/api/v1/storage/upload/document/{item.id}",
        files=file,
        data=form_data
    )
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["bucket_name"] == ItemDocuments.name
    assert data["description"] == "Test document"
    assert data["item_id"] == str(item.id)


def test_list_user_files(client, test_db, superuser_id):
    """Test pour la liste des fichiers d'un utilisateur"""
    # Créer des fichiers de test dans la base de données
    files = [
        FileMetadata(
            id=uuid.uuid4(),
            owner_id=superuser_id,
            filename=f"test{i}.txt",
            content_type="text/plain",
            size=100,
            bucket_name="test-bucket",
            path=f"test/{superuser_id}/test{i}.txt"
        )
        for i in range(3)
    ]
    
    for file in files:
        test_db.add(file)
    
    test_db.commit()
    
    # Appeler l'endpoint
    response = client.get("/api/v1/storage/files")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for i, file_data in enumerate(data):
        assert file_data["filename"] == f"test{i}.txt"
        assert file_data["owner_id"] == str(superuser_id)


def test_get_file_metadata(client, test_db, superuser_id):
    """Test pour la récupération des métadonnées d'un fichier"""
    # Créer un fichier de test dans la base de données
    file_id = uuid.uuid4()
    
    file = FileMetadata(
        id=file_id,
        owner_id=superuser_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path=f"test/{superuser_id}/test.txt"
    )
    
    test_db.add(file)
    test_db.commit()
    
    # Appeler l'endpoint
    response = client.get(f"/api/v1/storage/file/{file_id}")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(file_id)
    assert data["filename"] == "test.txt"
    assert data["owner_id"] == str(superuser_id)


def test_get_file_url(client, test_db, superuser_id):
    """Test pour la génération d'une URL de téléchargement"""
    # Créer un fichier de test dans la base de données
    file_id = uuid.uuid4()
    
    file = FileMetadata(
        id=file_id,
        owner_id=superuser_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path=f"test/{superuser_id}/test.txt"
    )
    
    test_db.add(file)
    test_db.commit()
    
    # Appeler l'endpoint
    response = client.get(f"/api/v1/storage/file/{file_id}/url")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "expires_in" in data
    assert data["expires_in"] == 60  # Valeur par défaut


def test_update_file_metadata(client, test_db, superuser_id):
    """Test pour la mise à jour des métadonnées d'un fichier"""
    # Créer un fichier de test dans la base de données
    file_id = uuid.uuid4()
    
    file = FileMetadata(
        id=file_id,
        owner_id=superuser_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path=f"test/{superuser_id}/test.txt",
        description="Original description"
    )
    
    test_db.add(file)
    test_db.commit()
    
    # Données à mettre à jour
    update_data = {
        "filename": "updated.txt",
        "description": "Updated description"
    }
    
    # Appeler l'endpoint
    response = client.put(
        f"/api/v1/storage/file/{file_id}",
        json=update_data
    )
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(file_id)
    assert data["filename"] == "updated.txt"  # Valeur mise à jour
    assert data["description"] == "Updated description"  # Valeur mise à jour


def test_delete_file(client, test_db, superuser_id):
    """Test pour la suppression d'un fichier"""
    # Créer un fichier de test dans la base de données
    file_id = uuid.uuid4()
    
    file = FileMetadata(
        id=file_id,
        owner_id=superuser_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path=f"test/{superuser_id}/test.txt"
    )
    
    test_db.add(file)
    test_db.commit()
    
    # Appeler l'endpoint
    response = client.delete(f"/api/v1/storage/file/{file_id}")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Vérifier que le fichier a été supprimé de la base de données
    file_in_db = test_db.get(FileMetadata, file_id)
    assert file_in_db is None


def test_file_not_found(client):
    """Test pour le cas où un fichier n'est pas trouvé"""
    # ID de fichier qui n'existe pas
    non_existent_id = uuid.uuid4()
    
    # Appeler l'endpoint
    response = client.get(f"/api/v1/storage/file/{non_existent_id}")
    
    # Vérifier la réponse
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_invalid_file_type(client):
    """Test pour le cas où un type de fichier invalide est uploadé"""
    # Fichier avec un type MIME non autorisé pour les images de profil
    file_content = b"test executable content"
    file = {"file": ("test.exe", file_content, "application/x-msdownload")}
    
    # Appeler l'endpoint
    with patch('app.api.routes.storage.StorageService.upload_file') as mock_upload:
        # Configurer le mock pour lever une HTTPException
        from fastapi import HTTPException
        mock_upload.side_effect = HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
        
        response = client.post(
            "/api/v1/storage/upload/profile-picture",
            files=file
        )
    
    # Vérifier la réponse
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
