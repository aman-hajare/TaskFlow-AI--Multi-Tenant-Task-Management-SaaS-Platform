import logging
import sys
import time
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("taskflow")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ"
    )

    logging.Formatter.converter = time.gmtime

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        "app.log", maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

# 2026-03-14 10:02:21 | INFO | taskflow | User created task 45