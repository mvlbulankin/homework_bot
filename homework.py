from http import HTTPStatus
from requests import HTTPError, RequestException
import logging
import os
import requests
import time

from dotenv import load_dotenv
from telegram import Bot

from exceptions import EnvironmentsMissingException, NotForSendException
from setup_logging import logger


load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


def send_message(bot, message):
    """Sends a message to Telegram chat."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f"Chat message {TELEGRAM_CHAT_ID}: {message}")
    except RequestException:
        raise RequestException("Error sending message to telegram")


def get_api_answer(current_timestamp):
    """Makes a request to a single API service endpoint."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception as error:
        raise HTTPError(f"Error requesting the main API: {error}")
    if homework_statuses.status_code != HTTPStatus.OK:
        status_code = homework_statuses.status_code
        raise HTTPError(f"Ошибка {status_code}")
    return homework_statuses.json()


def check_response(response):
    """Checks the API response for correctness."""
    if not isinstance(response, dict):
        raise TypeError("API response is different from dict")
    if "homeworks" not in response:
        raise KeyError("Dictionary error on homeworks key")
    list_works = response["homeworks"]
    if len(list_works) <= 0:
        raise IndexError("Homework list is empty")
    homework = list_works[0]
    return homework


def parse_status(homework):
    """Parses the status of this homework."""
    if "homework_name" not in homework:
        raise KeyError('Missing "homework_name" key in API response')
    if "status" not in homework:
        raise KeyError('Missing "status" key in API response')
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f"Unknown job status: {homework_status}")
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checks the availability of environment variables."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """The main logic of the bot."""
    status = ""
    error_cache_message = ""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical("One or more environments are missing")
        raise EnvironmentsMissingException(
            "One or more environments are missing"
        )
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get("current_date")
            message = parse_status(check_response(response))
            if message != status:
                send_message(bot, message)
                status = message
            time.sleep(RETRY_TIME)
        except NotForSendException as error:
            message = f"Program crash: {error}"
            logging.error(message)
        except Exception as error:
            logger.error(error)
            message_error = str(error)
            if message_error != error_cache_message:
                send_message(bot, message_error)
                error_cache_message = message_error
        time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
