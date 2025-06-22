import asyncio
from fastapi import FastAPI, HTTPException
from typing import List
from payments_service.presentation.routes import router
from payments_service.infrastructure.messaging import start_payment_consumer, start_outbox_publisher
from payments_service.infrastructure.models import Base
from payments_service.infrastructure.db import engine
from payments_service.logger import get_logger

from sqlalchemy.exc import SQLAlchemyError
logger = get_logger(__name__, filename="main.log")
app = FastAPI()
_tasks: List[asyncio.Task] = []
app.include_router(router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
    # запускаем фонового подписчика
    t1 = asyncio.create_task(start_payment_consumer(), name="payment_consumer")
    t2 = asyncio.create_task(start_outbox_publisher(), name="outbox_publisher")
    _tasks.extend([t1, t2])
    logger.info("✅ Background tasks started: outbox_publisher, payment_consumer")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🔴 Shutting down background tasks…")
    for t in _tasks:
        t.cancel()
    await asyncio.gather(*_tasks, return_exceptions=True)
    logger.info("🔴 All background tasks stopped")


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Простой endpoint для проверки:
    - API отвечает
    - База данных доступна
    """
    # Проверим соединение с базой (asyncpg)
    try:
        async with engine.begin() as conn:
            # выполнит простой SQL — если DB недоступна, упадёт
            await conn.execute("SELECT 1")
    except SQLAlchemyError as e:
        # если не смогли подключиться — вернём 503
        raise HTTPException(status_code=503, detail="DB connection failed")

    return {"status": "ok"}