from sqlmodel import SQLModel
from .item import Item
from .user import User
from .profile import Profile, ProfilePicturesBucket

# Pour Alembic
Base = SQLModel

__all__ = ["User", "Item", "Base", "Profile", "ProfilePicturesBucket"]

STORAGE_BUCKETS = [
    ProfilePicturesBucket,
    # Ajoutez d'autres buckets ici...
]
