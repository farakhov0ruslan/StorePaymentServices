# orders_service/infrastructure/messaging.py

import asyncio
import json
import aio_pika
from sqlalchemy import select

from orders_service.logger import get_logger
from orders_service.config import settings
from orders_service.infrastructure.db import AsyncSessionLocal
from orders_service.infrastructure.models import OutboxModel, OrderModel
from orders_service.domain.entities import OrderStatus

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
                res = await session.execute(select(OutboxModel).limit(10))
                events = res.scalars().all()
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


async def start_payment_result_consumer():
    """
    Фоновая задача:
    - подписывается на очередь payment_success и payment_failed,
    - для каждого сообщения меняет статус соответствующего заказа в БД.
    """
    conn = await aio_pika.connect_robust(settings.BROKER_URL)
    channel = await conn.channel()
    logger.info("🔄 Payment-result consumer starting, broker=%s", settings.BROKER_URL)

    # Подписываемся на обе очереди
    success_q = await channel.declare_queue(settings.PAYMENT_SUCCESS_QUEUE, durable=True)
    failed_q = await channel.declare_queue(settings.PAYMENT_FAILED_QUEUE, durable=True)
    logger.info("✅ Queues declared: %s, %s",
                settings.PAYMENT_SUCCESS_QUEUE, settings.PAYMENT_FAILED_QUEUE)

    async def _process(msg: aio_pika.IncomingMessage, new_status: OrderStatus):
        async with msg.process():
            logger.info("⬇ Received message %s from queue '%s'", msg.message_id, msg.routing_key)
            data = json.loads(msg.body)
            order_id = data.get("order_id")
            async with AsyncSessionLocal() as session:
                # ищем заказ, обновляем статус
                order = await session.get(OrderModel, order_id)
                if order and order.status != new_status:
                    logger.info("🔄 Updating order %s status: %s → %s",
                                order_id, order.status, new_status)
                    order.status = new_status
                    await session.commit()

    try:
        # Конкурентно слушаем обе очереди
        await success_q.consume(lambda msg: _process(msg, OrderStatus.PAID), no_ack=False)
        await failed_q.consume(lambda msg: _process(msg, OrderStatus.FAILED), no_ack=False)

        logger.info("🟢 Consumers started on %s and %s",
                    settings.PAYMENT_SUCCESS_QUEUE, settings.PAYMENT_FAILED_QUEUE)
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("🛑 Payment-result consumer cancelled, closing connection")
        await channel.close()
        await conn.close()
        raise
