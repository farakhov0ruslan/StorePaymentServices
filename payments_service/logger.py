import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.getenv("LOG_DIR", "/var/log/service")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str, filename: str = None) -> logging.Logger:
    """
    Создаёт логгер с ротацией файлов и выводом в консоль.
    - name: имя логгера (обычно __name__ модуля).
    - filename: имя файла лога внутри LOG_DIR. По умолчанию <name>.log.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Форматтер: время, уровень, модуль, сообщение
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-5s [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler с ротацией
    log_file = filename or f"{name}.log"
    file_path = os.path.join(LOG_DIR, log_file)
    fh = RotatingFileHandler(
        file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console Handler для вывода в stdout
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
