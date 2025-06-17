# orders_service/tests/conftest.py
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from orders_service.main import app
from orders_service.infrastructure.db import engine
from orders_service.infrastructure.models import Base

@pytest.fixture(scope="session")
def anyio_backend():
    # Чтобы любой async-фикстуре был доступен бэкенд asyncio
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def init_db():
    # Создаём схему БД один раз перед всеми тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Опционально: дропаем таблицы по завершении сессии
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_client(init_db):
    # ASGITransport направляет запросы прямо в FastAPI-приложение
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
