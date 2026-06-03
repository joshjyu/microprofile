import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

import app.routers.profiles as profiles_module
from main import app


@pytest_asyncio.fixture
async def client(monkeypatch):
    """
    Async test client with a mock MongoDB collection injected.

    Parameters:
      monkeypatch: pytest fixture for temporary attribute replacement.
    Returns:
      An AsyncClient pointed at the test app.
    """
    mock_collection = AsyncMongoMockClient()["test"]["profiles"]
    monkeypatch.setattr(profiles_module, "profiles", mock_collection)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
