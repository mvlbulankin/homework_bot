from logging.handlers import RotatingFileHandler
import logging


logging.basicConfig(
    level=logging.DEBUG,
    filename="main.log",
    format="%(funcName)s, %(lineno)s, %(levelname)s, %(message)s",
    filemode="w",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    "my_logger.log", encoding="UTF-8", maxBytes=50000000, backupCount=5
)
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s"
)
handler.setFormatter(formatter)
