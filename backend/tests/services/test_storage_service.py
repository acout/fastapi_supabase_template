import io
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.file import FileMetadata
from app.models.storage import ProfilePictures
from app.services.storage import StorageService

# Créer un moteur de base de données en mémoire pour les tests
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture
def db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def mock_supabase_client():
    """Mock pour le client Supabase"""
    client = AsyncMock()
    
    # Configurer le mock pour storage.from_().upload()
    storage_from = AsyncMock()
    storage_from.upload.return_value = {"Key": "test/path/test.txt"}
    storage_from.create_signed_url.return_value = "https://example.com/test.txt?signature=abc"
    storage_from.download.return_value = b"test content"
    storage_from.remove.return_value = True
    storage_from.list.return_value = [
        {"name": "test1.txt", "id": "123", "metadata": {}},
        {"name": "test2.txt", "id": "456", "metadata": {}}
    ]
    
    # Configurer client.storage.from_()
    client.storage.from_.return_value = storage_from
    
    # Configurer client.storage.list_buckets()
    client.storage.list_buckets.return_value = [{"name": "existing-bucket"}]
    
    # Configurer client.storage.create_bucket()
    client.storage.create_bucket.return_value = {"name": "new-bucket"}
    
    return client


@pytest.fixture
def storage_service(mock_supabase_client):
    """Service de stockage avec un client mock"""
    return StorageService(mock_supabase_client)


@pytest.fixture
def mock_upload_file():
    """Mock pour UploadFile"""
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    file.content_type = "text/plain"
    file.read = AsyncMock(return_value=b"test content")
    file.seek = AsyncMock()
    return file


@pytest.mark.asyncio
async def test_initialize_buckets(storage_service, mock_supabase_client):
    """Test d'initialisation des buckets"""
    # Buckets à initialiser
    class TestBucket1:
        name = "existing-bucket"
        public = True
    
    class TestBucket2:
        name = "new-bucket"
        public = False
    
    # Exécuter l'initialisation
    await storage_service.initialize_buckets([TestBucket1, TestBucket2])
    
    # Vérifier que list_buckets a été appelé
    mock_supabase_client.storage.list_buckets.assert_called_once()
    
    # Vérifier que create_bucket a été appelé une seule fois pour le nouveau bucket
    assert mock_supabase_client.storage.create_bucket.call_count == 1
    mock_supabase_client.storage.create_bucket.assert_called_with(
        "new-bucket", public=False
    )


@pytest.mark.asyncio
async def test_upload_file(storage_service, mock_supabase_client, mock_upload_file, db):
    """Test d'upload de fichier"""
    # Données pour le test
    user_id = uuid.uuid4()
    record_id = uuid.uuid4()
    description = "Test description"
    
    # Exécuter l'upload
    path, file_meta = await storage_service.upload_file(
        bucket_class=ProfilePictures,
        file=mock_upload_file,
        user_id=user_id,
        record_id=record_id,
        description=description,
        session=db
    )
    
    # Vérifier que from_ et upload ont été appelés
    mock_supabase_client.storage.from_.assert_called_with(ProfilePictures.name)
    mock_supabase_client.storage.from_.return_value.upload.assert_called_once()
    
    # Vérifier que le fichier a été lu
    mock_upload_file.read.assert_called_once()
    
    # Vérifier les métadonnées
    assert isinstance(file_meta, FileMetadata)
    assert file_meta.owner_id == user_id
    assert file_meta.item_id == record_id
    assert file_meta.filename == "test.txt"
    assert file_meta.content_type == "text/plain"
    assert file_meta.bucket_name == ProfilePictures.name
    assert file_meta.description == description


@pytest.mark.asyncio
async def test_upload_file_invalid_type(storage_service, mock_supabase_client):
    """Test d'upload avec un type de fichier non autorisé"""
    # Mock fichier avec type non autorisé
    file = MagicMock(spec=UploadFile)
    file.filename = "test.exe"
    file.content_type = "application/x-msdownload"  # Type non autorisé
    
    # Essayer d'uploader avec une classe qui n'autorise que les images
    with pytest.raises(HTTPException) as exc_info:
        await storage_service.upload_file(
            bucket_class=ProfilePictures,  # N'accepte que les images
            file=file,
            user_id=uuid.uuid4()
        )
    
    # Vérifier l'exception
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_file_too_large(storage_service, mock_supabase_client):
    """Test d'upload avec un fichier trop grand"""
    # Mock fichier trop grand
    file = MagicMock(spec=UploadFile)
    file.filename = "test.jpg"
    file.content_type = "image/jpeg"
    # Taille supérieure à la limite de ProfilePictures (5MB)
    file.read = AsyncMock(return_value=b"a" * (6 * 1024 * 1024))
    
    # Essayer d'uploader
    with pytest.raises(HTTPException) as exc_info:
        await storage_service.upload_file(
            bucket_class=ProfilePictures,
            file=file,
            user_id=uuid.uuid4()
        )
    
    # Vérifier l'exception
    assert exc_info.value.status_code == 400
    assert "File too large" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_file_url(storage_service, mock_supabase_client):
    """Test de génération d'URL signée"""
    # Paramètres
    bucket_name = "test-bucket"
    file_path = "test/path/test.txt"
    expiration = 120
    
    # Obtenir l'URL
    url = await storage_service.get_file_url(bucket_name, file_path, expiration)
    
    # Vérifier l'appel
    mock_supabase_client.storage.from_.assert_called_with(bucket_name)
    mock_supabase_client.storage.from_.return_value.create_signed_url.assert_called_with(
        path=file_path, expires_in=expiration
    )
    
    # Vérifier la valeur de retour
    assert url == "https://example.com/test.txt?signature=abc"


@pytest.mark.asyncio
async def test_download_file(storage_service, mock_supabase_client):
    """Test de téléchargement de fichier"""
    # Paramètres
    bucket_name = "test-bucket"
    file_path = "test/path/test.txt"
    
    # Télécharger le fichier
    result = await storage_service.download_file(bucket_name, file_path)
    
    # Vérifier l'appel
    mock_supabase_client.storage.from_.assert_called_with(bucket_name)
    mock_supabase_client.storage.from_.return_value.download.assert_called_with(file_path)
    
    # Vérifier la valeur de retour
    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == b"test content"


@pytest.mark.asyncio
async def test_delete_file(storage_service, mock_supabase_client, db):
    """Test de suppression de fichier"""
    # Paramètres
    bucket_name = "test-bucket"
    file_path = "test/path/test.txt"
    
    # Créer des métadonnées de fichier
    file_id = uuid.uuid4()
    file_meta = FileMetadata(
        id=file_id,
        owner_id=uuid.uuid4(),
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name=bucket_name,
        path=file_path
    )
    db.add(file_meta)
    db.commit()
    
    # Supprimer le fichier
    result = await storage_service.delete_file(
        bucket_name=bucket_name,
        file_path=file_path,
        session=db,
        metadata_id=file_id
    )
    
    # Vérifier l'appel
    mock_supabase_client.storage.from_.assert_called_with(bucket_name)
    mock_supabase_client.storage.from_.return_value.remove.assert_called_with(file_path)
    
    # Vérifier la valeur de retour
    assert result is True
    
    # Vérifier que les métadonnées ont été supprimées
    assert db.get(FileMetadata, file_id) is None


@pytest.mark.asyncio
async def test_list_files(storage_service, mock_supabase_client):
    """Test de liste des fichiers"""
    # Paramètres
    bucket_name = "test-bucket"
    path = "test/path"
    
    # Lister les fichiers
    result = await storage_service.list_files(bucket_name, path)
    
    # Vérifier l'appel
    mock_supabase_client.storage.from_.assert_called_with(bucket_name)
    mock_supabase_client.storage.from_.return_value.list.assert_called_with(path)
    
    # Vérifier la valeur de retour
    assert len(result) == 2
    assert result[0]["name"] == "test1.txt"
    assert result[1]["name"] == "test2.txt"
