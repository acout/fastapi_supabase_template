from sqlmodel import SQLModel
from .item import Item
from .user import User
from .profile import Profile, ProfilePicturesBucket
from .file import FileMetadata
from .storage import ProfilePictures, ItemDocuments

# Pour Alembic
Base = SQLModel

__all__ = [
    "User", "Item", "Base", "Profile",
    "ProfilePicturesBucket", "FileMetadata",
    "ProfilePictures", "ItemDocuments"
]

STORAGE_BUCKETS = [
    ProfilePicturesBucket,
    ProfilePictures,
    ItemDocuments,
    # Ajoutez d'autres buckets ici...
]
