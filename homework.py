import logging
import os
import requests
import time

from dotenv import load_dotenv
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from telegram import Bot

from exceptions import ErrorSendException

load_dotenv()
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

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


def send_message(bot, message):
    """
    Sends a message to Telegram chat.

    """

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info("Chat message {TELEGRAM_CHAT_ID}: {message}")
    except ErrorSendException:
        logger.error("Error sending message to telegram")


def get_api_answer(current_timestamp):
    """
    Makes a request to a single API service endpoint.

    """

    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception as error:
        logging.error(f"Error requesting the main API: {error}")
        raise Exception(f"Error requesting the main API: {error}")
    if homework_statuses.status_code != HTTPStatus.OK:
        status_code = homework_statuses.status_code
        logging.error(f"Ошибка {status_code}")
        raise Exception(f"Ошибка {status_code}")
    try:
        return homework_statuses.json()
    except ValueError:
        logger.error("Error parsing response from json")
        raise ValueError("Error parsing response from json")


def check_response(response):
    """
    Checks the API response for correctness.

    """

    if type(response) is not dict:
        raise TypeError("API response is different from dict")
    try:
        list_works = response["homeworks"]
    except KeyError:
        logger.error("Dictionary error on homeworks key")
        raise KeyError("Dictionary error on homeworks key")
    try:
        homework = list_works[0]
    except IndexError:
        logger.error("Homework list is empty")
        raise IndexError("Homework list is empty")
    return homework


def parse_status(homework):
    """
    Parses the status of this work from
    information about a particular homework.

    """

    if type(homework) is dict:
        homework_name = homework.get("homework_name")
        homework_status = homework.get("status")
    if "homework_name" not in homework:
        raise KeyError('Missing "homework_name" key in API response')
    if "status" not in homework:
        raise Exception('Missing "status" key in API response')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f"Unknown job status: {homework_status}")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """
    Checks the availability of environment variables.

    """

    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    return False


def main():
    """
    The main logic of the bot.

    """

    status = ""
    error_cache_message = ""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical("One or more environments are missing")
        raise Exception("One or more environments are missing")
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get("current_date")
            message = parse_status(check_response(response))
            if message != status:
                send_message(bot, message)
                status = message
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(error)
            message_error = str(error)
            if message_error != error_cache_message:
                send_message(bot, message_error)
                error_cache_message = message_error
        time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
