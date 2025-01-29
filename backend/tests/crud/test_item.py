import uuid

import pytest
from faker import Faker
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.models.item import Item, ItemCreate, ItemUpdate

fake = Faker()


@pytest.mark.anyio
async def test_create_item(db: AsyncSession, test_user_id: uuid.UUID) -> None:
    """Test creating a new item"""
    title = fake.sentence(nb_words=3)
    description = fake.text(max_nb_chars=200)
    item_in = ItemCreate(title=title, description=description)

    item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_in)

    assert item.id is not None
    assert item.title == title
    assert item.description == description
    assert item.owner_id == test_user_id


@pytest.mark.anyio
async def test_get_item(db: AsyncSession, test_item: Item) -> None:
    """Test retrieving a single item"""
    stored_item = await crud.item.get(db, id=test_item.id)

    assert stored_item is not None
    assert stored_item.id == test_item.id
    assert stored_item.title == test_item.title
    assert stored_item.description == test_item.description
    assert stored_item.owner_id == test_item.owner_id


@pytest.mark.anyio
async def test_get_multi_items(db: AsyncSession, test_user_id: uuid.UUID) -> None:
    """Test retrieving multiple items"""
    # Create multiple items
    items = []
    for _ in range(5):
        item_in = ItemCreate(
            title=fake.sentence(nb_words=3), description=fake.text(max_nb_chars=200)
        )
        item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_in)
        items.append(item)
    # Retrieve multiple items
    stored_items = await crud.item.get_multi(db)
    assert len(stored_items) == 5
    # Verify all items are in the list
    for item in items:
        assert item in stored_items


@pytest.mark.anyio
async def test_update_item(db: AsyncSession, test_item: Item) -> None:
    """Test updating an item"""
    new_title = fake.sentence(nb_words=3)
    new_description = fake.text(max_nb_chars=200)
    update_data = ItemUpdate(title=new_title, description=new_description)

    updated_item = await crud.item.update(db, id=test_item.id, obj_in=update_data)

    assert updated_item is not None
    assert updated_item.id == test_item.id
    assert updated_item.title == new_title
    assert updated_item.description == new_description
    assert updated_item.owner_id == test_item.owner_id

    # update with empty data
    updated_item = await crud.item.update(db, id=uuid.uuid4(), obj_in=update_data)
    assert updated_item is None


@pytest.mark.anyio
async def test_delete_item(db: AsyncSession, test_item: Item) -> None:
    """Test deleting an item"""
    deleted_item = await crud.item.remove(db, id=test_item.id)
    assert deleted_item is not None
    assert deleted_item.id == test_item.id

    # Verify item is deleted
    item = await crud.item.get(db, id=test_item.id)
    assert item is None

    # delete empty items
    deleted_item = await crud.item.remove(db, id=test_item.id)
    assert deleted_item is None
