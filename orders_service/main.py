import asyncio
from typing import List
from fastapi import FastAPI
from orders_service.logger import get_logger
from orders_service.presentation.routes import router
from orders_service.infrastructure.db import engine
from orders_service.infrastructure.models import Base
from orders_service.infrastructure.messaging import (
    start_outbox_publisher,
    start_payment_result_consumer,
)

logger = get_logger(__name__, filename="main.log")

app = FastAPI(title="Order Service")
app.include_router(router)
_tasks: List[asyncio.Task] = []


@app.on_event("startup")
async def on_startup():
    # Создаём все таблицы
    logger.info("Starting up Order Service…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")

    t1 = asyncio.create_task(start_outbox_publisher(), name="outbox_publisher")
    t2 = asyncio.create_task(start_payment_result_consumer(), name="payment_result_consumer")
    _tasks.extend([t1, t2])
    logger.info("✅ Background tasks started: outbox_publisher, payment_result_consumer")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🔴 Shutting down background tasks…")
    for t in _tasks:
        t.cancel()
    # дождёмся, чтобы все они нормально закрыли соединения
    await asyncio.gather(*_tasks, return_exceptions=True)
    logger.info("🔴 All background tasks stopped")
