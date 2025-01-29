import uuid
from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.core.auth import get_super_client
from app.core.db import engine, init_db
from app.main import app
from app.models.item import Item, ItemCreate


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        await init_db(session)
        yield session
        statement = delete(Item)
        await session.exec(statement)  # type: ignore
        await session.commit()


@pytest.fixture(scope="module")
async def client():
    """async client fixture
    Ref: https://fastapi.tiangolo.com/advanced/async-tests/#example
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


fake = Faker()


@pytest.fixture(scope="function")
async def test_user_id(db: AsyncSession) -> AsyncGenerator[uuid.UUID, None]:
    """Fixture to create a test user"""

    super_client = await get_super_client()

    try:
        response = await super_client.auth.admin.create_user(
            {"email": fake.email(), "password": "testpassword123"}
        )
        yield uuid.UUID(response.user.id)
    finally:
        # clean users
        users = await super_client.auth.admin.list_users()
        for user in users:
            await super_client.auth.admin.delete_user(user.id)


@pytest.fixture(scope="function")
async def test_item(
    db: AsyncSession, test_user_id: uuid.UUID
) -> AsyncGenerator[Item, None]:
    """Fixture to create a test item and clean it up after the test"""
    item_in = ItemCreate(
        title=fake.sentence(nb_words=3), description=fake.text(max_nb_chars=200)
    )
    item = await crud.item.create(db, owner_id=test_user_id, obj_in=item_in)
    yield item


# @pytest.fixture(scope="module")
# async def token() -> AsyncGenerator[Token, None]:
#     url = os.environ.get("SUPABASE_TEST_URL")
#     assert url is not None, "Must provide SUPABASE_TEST_URL environment variable"
#     key = os.environ.get("SUPABASE_TEST_KEY")
#     assert key is not None, "Must provide SUPABASE_TEST_KEY environment variable"
#     db_client = await create_client(url, key)
#     fake_email = Faker().email()
#     fake_password = Faker().password()
#     response = await db_client.auth.sign_up(
#         {"email": fake_email, "password": fake_password}
#     )
#     assert response.user
#     assert response.user.email == fake_email
#     assert response.user.id is not None

#     yield Token(access_token=response.session.access_token)
