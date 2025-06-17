import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL",
                             "postgresql+asyncpg://order_user:order_pass@order_db:5432/order_db")

    BROKER_URL: str = os.getenv("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")

    PAYMENT_SUCCESS_QUEUE: str = os.getenv("PAYMENT_SUCCESS_QUEUE", "payment_success")

    PAYMENT_FAILED_QUEUE: str = os.getenv("PAYMENT_FAILED_QUEUE", "payment_failed")

    OUTBOX_POLL_INTERVAL: float = float(os.getenv("OUTBOX_POLL_INTERVAL", "1.0"))


settings = Settings()
