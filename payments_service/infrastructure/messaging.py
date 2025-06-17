import aio_pika
import json
import asyncio
from sqlalchemy import select

from payments_service.application.use_cases import ProcessPayment
from payments_service.config import settings
from payments_service.infrastructure.repository import SQLAccountRepo, SQLInboxRepo, SQLOutboxRepo
from payments_service.logger import get_logger
from payments_service.infrastructure.db import AsyncSessionLocal
from payments_service.infrastructure.models import OutboxModel

logger = get_logger(__name__, filename="messaging.log")


async def start_outbox_publisher():
    """
    Фоновая задача:
    - читает из таблицы outbox пачками (limit=10),
    - публикует каждое событие в RabbitMQ с routing_key=event_type,
    - удаляет отправленные записи из outbox.
    """
    logger.info("🔄 Outbox publisher starting, broker=%s", settings.BROKER_URL)
    conn = await aio_pika.connect_robust(settings.BROKER_URL)
    channel = await conn.channel()
    try:
        while True:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(OutboxModel).limit(10))
                events = result.scalars().all()
                for ev in events:
                    logger.info("📤 Publishing event %s of type '%s'", ev.id, ev.event_type)
                    msg = aio_pika.Message(body=ev.payload.encode())
                    await channel.default_exchange.publish(msg, routing_key=ev.event_type)
                    await session.delete(ev)

                await session.commit()

            await asyncio.sleep(settings.OUTBOX_POLL_INTERVAL)
    except asyncio.CancelledError:
        logger.info("🛑 Outbox publisher cancelled, closing connection")
        await channel.close()
        await conn.close()
        raise

async def start_payment_consumer():
    conn = await aio_pika.connect_robust(settings.BROKER_URL)
    channel = await conn.channel()
    queue = await channel.declare_queue(settings.ORDER_CREATED_QUEUE, durable=True)
    logger.info("🟢 Connected to broker, listening on queue %r", settings.ORDER_CREATED_QUEUE)
    try:
        async for msg in queue:
            async with msg.process():
                data = json.loads(msg.body)
                logger.debug("⬇ Received message %s: %s", msg.message_id, data)
                uc = ProcessPayment(SQLAccountRepo(), SQLInboxRepo(), SQLOutboxRepo())
                await uc.execute(msg.message_id, data["user_id"], data["order_id"], data["amount"])
                logger.info(
                    "✅ Processed payment for message %s => user=%s, amount=%.2f",
                    msg.message_id,
                    data["user_id"],
                    data["amount"],
                )
    except asyncio.CancelledError:
        logger.info("🛑 Payment consumer cancelled, closing connection")
        await channel.close()
        await conn.close()
        raise