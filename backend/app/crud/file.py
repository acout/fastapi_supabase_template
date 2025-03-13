import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.file import FileMetadata, FileMetadataCreate, FileMetadataUpdate


class CRUDFileMetadata(CRUDBase[FileMetadata, FileMetadataCreate, FileMetadataUpdate]):
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: FileMetadataCreate
    ) -> FileMetadata:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: FileMetadataUpdate
    ) -> FileMetadata | None:
        db_obj = super().get(session, id=id)
        if db_obj:
            # Mettre à jour updated_at
            update_data = obj_in.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()

            # Mettre à jour l'objet
            db_obj.sqlmodel_update(update_data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def get_by_item_id(
        self, session: Session, *, item_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[FileMetadata]:
        """Récupérer les fichiers associés à un item"""
        statement = (
            select(self.model)
            .where(self.model.item_id == item_id)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[FileMetadata]:
        """Récupérer les fichiers d'un utilisateur"""
        statement = (
            select(self.model)
            .where(self.model.owner_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_by_bucket(
        self, session: Session, *, bucket_name: str, skip: int = 0, limit: int = 100
    ) -> list[FileMetadata]:
        """Récupérer les fichiers dans un bucket spécifique"""
        statement = (
            select(self.model)
            .where(self.model.bucket_name == bucket_name)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))


file_metadata = CRUDFileMetadata(FileMetadata)
