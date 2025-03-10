import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import RLSModel


class FileMetadataBase(SQLModel):
    """Modèle de base pour les métadonnées de fichier"""
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    size: int = Field(gt=0)
    bucket_name: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=512)
    description: Optional[str] = Field(default=None, max_length=255)


class FileMetadataCreate(FileMetadataBase):
    """Schéma pour la création de métadonnées de fichier"""
    item_id: Optional[uuid.UUID] = None


class FileMetadataUpdate(SQLModel):
    """Schéma pour la mise à jour de métadonnées de fichier"""
    filename: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class FileMetadata(RLSModel, FileMetadataBase, table=True):
    """Modèle de table pour les métadonnées de fichier"""
    item_id: Optional[uuid.UUID] = Field(default=None, foreign_key="item.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FileMetadataPublic(FileMetadataBase):
    """Schéma pour les métadonnées de fichier à retourner via l'API"""
    id: uuid.UUID
    owner_id: uuid.UUID
    item_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class FileMetadataListPublic(SQLModel):
    """Schéma pour la liste de métadonnées de fichier à retourner via l'API"""
    data: list[FileMetadataPublic]
    count: int
