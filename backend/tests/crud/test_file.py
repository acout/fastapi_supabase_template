import uuid
from datetime import datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.crud.file import file_metadata
from app.models.file import FileMetadata, FileMetadataCreate, FileMetadataUpdate

# Créer un moteur de base de données en mémoire pour les tests
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture
def db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_file_metadata(db):
    """Test de création de métadonnées de fichier"""
    # Données pour la création
    owner_id = uuid.uuid4()
    item_id = uuid.uuid4()
    file_data = FileMetadataCreate(
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/test.txt",
        description="Test description",
        item_id=item_id,
    )

    # Créer les métadonnées
    file_meta = file_metadata.create(db, owner_id=owner_id, obj_in=file_data)

    # Vérifier les données
    assert file_meta.filename == "test.txt"
    assert file_meta.content_type == "text/plain"
    assert file_meta.size == 100
    assert file_meta.bucket_name == "test-bucket"
    assert file_meta.path == "test/path/test.txt"
    assert file_meta.description == "Test description"
    assert file_meta.owner_id == owner_id
    assert file_meta.item_id == item_id
    assert isinstance(file_meta.id, uuid.UUID)
    assert isinstance(file_meta.created_at, datetime)
    assert isinstance(file_meta.updated_at, datetime)


def test_get_file_metadata(db):
    """Test de récupération de métadonnées de fichier"""
    # Créer un fichier de test
    file_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    file_meta = FileMetadata(
        id=file_id,
        owner_id=owner_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/test.txt",
        description="Test description",
    )
    db.add(file_meta)
    db.commit()

    # Récupérer les métadonnées
    retrieved_meta = file_metadata.get(db, id=file_id)

    # Vérifier les données
    assert retrieved_meta is not None
    assert retrieved_meta.id == file_id
    assert retrieved_meta.owner_id == owner_id
    assert retrieved_meta.filename == "test.txt"


def test_update_file_metadata(db):
    """Test de mise à jour de métadonnées de fichier"""
    # Créer un fichier de test
    file_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    created_at = datetime.utcnow() - timedelta(
        days=1
    )  # Date antérieure pour tester updated_at
    file_meta = FileMetadata(
        id=file_id,
        owner_id=owner_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/test.txt",
        description="Original description",
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(file_meta)
    db.commit()

    # Données pour la mise à jour
    update_data = FileMetadataUpdate(
        filename="updated.txt", description="Updated description"
    )

    # Mettre à jour les métadonnées
    updated_meta = file_metadata.update(db, id=file_id, obj_in=update_data)

    # Vérifier les données
    assert updated_meta is not None
    assert updated_meta.id == file_id
    assert updated_meta.filename == "updated.txt"  # Mise à jour
    assert updated_meta.description == "Updated description"  # Mise à jour
    assert updated_meta.content_type == "text/plain"  # Inchangé
    assert updated_meta.created_at == created_at  # Inchangé
    assert updated_meta.updated_at > created_at  # Mis à jour


def test_delete_file_metadata(db):
    """Test de suppression de métadonnées de fichier"""
    # Créer un fichier de test
    file_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    file_meta = FileMetadata(
        id=file_id,
        owner_id=owner_id,
        filename="test.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/test.txt",
    )
    db.add(file_meta)
    db.commit()

    # Supprimer les métadonnées
    removed_meta = file_metadata.remove(db, id=file_id)

    # Vérifier que la suppression a réussi
    assert removed_meta is not None
    assert removed_meta.id == file_id

    # Vérifier que le fichier n'existe plus dans la base de données
    retrieved_meta = file_metadata.get(db, id=file_id)
    assert retrieved_meta is None


def test_get_by_item_id(db):
    """Test de récupération des fichiers par item_id"""
    # Créer un ID d'item
    item_id = uuid.uuid4()
    owner_id = uuid.uuid4()

    # Créer plusieurs fichiers associés à cet item
    files = [
        FileMetadata(
            id=uuid.uuid4(),
            owner_id=owner_id,
            filename=f"test{i}.txt",
            content_type="text/plain",
            size=100,
            bucket_name="test-bucket",
            path=f"test/path/test{i}.txt",
            item_id=item_id,
        )
        for i in range(3)
    ]

    # Créer un fichier associé à un autre item
    other_file = FileMetadata(
        id=uuid.uuid4(),
        owner_id=owner_id,
        filename="other.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/other.txt",
        item_id=uuid.uuid4(),  # ID différent
    )

    # Ajouter tous les fichiers à la base de données
    for file in files + [other_file]:
        db.add(file)
    db.commit()

    # Récupérer les fichiers par item_id
    retrieved_files = file_metadata.get_by_item_id(db, item_id=item_id)

    # Vérifier les données
    assert len(retrieved_files) == 3
    for i, file in enumerate(retrieved_files):
        assert file.filename == f"test{i}.txt"
        assert file.item_id == item_id


def test_get_by_user_id(db):
    """Test de récupération des fichiers par user_id (owner_id)"""
    # Créer un ID d'utilisateur
    user_id = uuid.uuid4()

    # Créer plusieurs fichiers appartenant à cet utilisateur
    files = [
        FileMetadata(
            id=uuid.uuid4(),
            owner_id=user_id,
            filename=f"test{i}.txt",
            content_type="text/plain",
            size=100,
            bucket_name="test-bucket",
            path=f"test/path/test{i}.txt",
        )
        for i in range(3)
    ]

    # Créer un fichier appartenant à un autre utilisateur
    other_file = FileMetadata(
        id=uuid.uuid4(),
        owner_id=uuid.uuid4(),  # ID différent
        filename="other.txt",
        content_type="text/plain",
        size=100,
        bucket_name="test-bucket",
        path="test/path/other.txt",
    )

    # Ajouter tous les fichiers à la base de données
    for file in files + [other_file]:
        db.add(file)
    db.commit()

    # Récupérer les fichiers par user_id
    retrieved_files = file_metadata.get_by_user_id(db, user_id=user_id)

    # Vérifier les données
    assert len(retrieved_files) == 3
    for i, file in enumerate(retrieved_files):
        assert file.filename == f"test{i}.txt"
        assert file.owner_id == user_id


def test_get_by_bucket(db):
    """Test de récupération des fichiers par bucket_name"""
    # Créer un nom de bucket
    bucket_name = "test-bucket"
    owner_id = uuid.uuid4()

    # Créer plusieurs fichiers dans ce bucket
    files = [
        FileMetadata(
            id=uuid.uuid4(),
            owner_id=owner_id,
            filename=f"test{i}.txt",
            content_type="text/plain",
            size=100,
            bucket_name=bucket_name,
            path=f"test/path/test{i}.txt",
        )
        for i in range(3)
    ]

    # Créer un fichier dans un autre bucket
    other_file = FileMetadata(
        id=uuid.uuid4(),
        owner_id=owner_id,
        filename="other.txt",
        content_type="text/plain",
        size=100,
        bucket_name="other-bucket",  # Nom différent
        path="test/path/other.txt",
    )

    # Ajouter tous les fichiers à la base de données
    for file in files + [other_file]:
        db.add(file)
    db.commit()

    # Récupérer les fichiers par bucket_name
    retrieved_files = file_metadata.get_by_bucket(db, bucket_name=bucket_name)

    # Vérifier les données
    assert len(retrieved_files) == 3
    for i, file in enumerate(retrieved_files):
        assert file.filename == f"test{i}.txt"
        assert file.bucket_name == bucket_name
