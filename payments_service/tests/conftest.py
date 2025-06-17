# payments_service/tests/conftest.py

import pytest
from httpx import AsyncClient, ASGITransport
from payments_service.main import app
from payments_service.infrastructure.db import engine
from payments_service.infrastructure.models import Base


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    # создаём все таблицы один раз перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # по желанию — чистим после всех тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client(init_db):
    # клиент, который шлёт запросы прямо в FastAPI-приложение
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
