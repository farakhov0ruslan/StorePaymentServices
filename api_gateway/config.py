import os


class Settings:
    ORDER_SERVICE_URL: str = os.getenv("ORDER_SERVICE_URL", "http://order_service:80")
    PAYMENT_SERVICE_URL: str = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:80")

settings = Settings()
