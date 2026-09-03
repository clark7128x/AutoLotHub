import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User, Role
from uuid import uuid4
from unittest.mock import AsyncMock

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture(autouse=True)
def override_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user():
    user = User(id=uuid4(), email="admin@test.com", is_active=True)
    user.roles = [Role(name="Admin")]
    return user

@pytest.fixture
def dealer_user():
    user = User(id=uuid4(), email="dealer@test.com", is_active=True)
    user.roles = [Role(name="Dealer")]
    return user

@pytest_asyncio.fixture
async def admin_client(admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.pop(get_current_user, None)

@pytest_asyncio.fixture
async def dealer_client(dealer_user):
    app.dependency_overrides[get_current_user] = lambda: dealer_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.pop(get_current_user, None)
