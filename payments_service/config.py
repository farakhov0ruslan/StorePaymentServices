import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL",
                                  "postgresql+asyncpg://payment_user:payment_pass@payment_db:5432/payment_db")

    BROKER_URL: str = os.getenv("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")

    ORDER_CREATED_QUEUE: str = os.getenv("ORDER_CREATED_QUEUE", "order_created")

    OUTBOX_POLL_INTERVAL: float = float(os.getenv("OUTBOX_POLL_INTERVAL", 1))


settings = Settings()
