from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine
from app.main import app


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        async with session.begin():
            yield session
        await session.rollback()


@pytest.fixture(scope="module")
async def client():
    """async client fixture
    Ref: https://fastapi.tiangolo.com/advanced/async-tests/#example
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


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
