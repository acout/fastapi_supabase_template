from .item import Item
from .user import User
from sqlmodel import SQLModel
__all__ = ["User", "Item", "Message"]


# Generic message
class Message(SQLModel):
    message: str
