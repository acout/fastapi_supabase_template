import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import CRUDBase
from app.models.item import Item, ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create(
        self, session: AsyncSession, *, owner_id: uuid.UUID, obj_in: ItemCreate
    ) -> Item:
        return await super().create(session, owner_id=owner_id, obj_in=obj_in)

    async def update(
        self, session: AsyncSession, *, id: uuid.UUID, obj_in: ItemUpdate
    ) -> Item | None:
        return await super().update(session, id=id, obj_in=obj_in)


item = CRUDItem(Item)
