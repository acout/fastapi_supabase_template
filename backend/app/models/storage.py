from typing import ClassVar, List, Optional

from app.models.base import StorageBucket
from app.models.item import Item


class ProfilePictures(StorageBucket):
    """Bucket pour stocker les images de profil des utilisateurs."""
    name: ClassVar[str] = "profile-pictures"
    public: ClassVar[bool] = True
    allowed_mime_types: ClassVar[List[str]] = ["image/jpeg", "image/png", "image/gif"]
    max_file_size: ClassVar[int] = 5 * 1024 * 1024  # 5MB

    @classmethod
    def get_path_pattern(cls) -> str:
        """Personnalisation du pattern de chemin."""
        return "{user_id}/profile/{filename}"


class ItemDocuments(StorageBucket):
    """Bucket pour stocker les documents liés aux items."""
    name: ClassVar[str] = "item-documents"
    public: ClassVar[bool] = False
    allowed_mime_types: ClassVar[List[str]] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/csv"
    ]
    max_file_size: ClassVar[int] = 10 * 1024 * 1024  # 10MB
    linked_model: ClassVar[Optional[type]] = Item

    @classmethod
    def get_path_pattern(cls) -> str:
        """Personnalisation du pattern de chemin."""
        return "items/{record_id}/documents/{filename}"
