import os
from time import sleep

import requests
import telegram
from loguru import logger
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telegram.Bot(os.getenv('BOT_TOKEN'))


def debug_only(record):
    return record["level"].name == "DEBUG"


def info_only(record):
    return record["level"].name == "INFO"


logger.add(
    'debug.log',
    format='{level}::{time}::{message}',
    level='DEBUG',
    filter=debug_only,
    rotation='0:00',
    compression='zip',
)
logger.add(
    'info.log',
    format='{level}::{time}::{message}',
    level='INFO',
    filter=info_only,
    rotation='0:00',
    compression='zip',
)
logger.add(
    'error.log',
    format='{level}::{time}::{message}',
    level='ERROR',
    rotation='0:00',
    compression='zip',
)


def get_chat_id():
    """Get user chat_id"""
    try:
        chat_id = bot.get_updates()[-1].message.chat_id
    except Exception as e:
        logger.error(e)
        chat_id = None
    return chat_id


def send_message(response, chat_id):
    """Sending message to user"""
    attempt = response.json().get('new_attempts')[0]
    title = attempt.get('lesson_title')
    lesson_link = attempt.get('lesson_url')
    logger.info(response.json())
    if attempt.get('is_negative'):
        teacher_result = 'К сожалению, в работе нашлись ошибки.'
    else:
        teacher_result = 'Преподавателю всё понравилось, ' \
                         'можно приступать к следующему уроку!'
    message_text = f'У вас проверили работу "{title}".\n' \
                   f'{teacher_result}\n' \
                   f'{lesson_link}'

    bot.send_message(chat_id=chat_id, text=message_text)


def request_check():
    """Check lesson status"""
    chat_id = params = None
    headers = {'Authorization': os.getenv('DEVMAN_TOKEN')}
    url = 'https://dvmn.org/api/long_polling/'
    while True:
        if not chat_id:
            chat_id = get_chat_id()
            logger.info(f'Chat ID = {chat_id}')
        else:
            try:
                if params:
                    response = requests.get(
                        url=url, headers=headers, params=params
                    )
                else:
                    response = requests.get(url=url, headers=headers)
                logger.debug(response.url)
                if response.json().get('status') == 'found':
                    send_message(response, chat_id)
                    params = None
                elif response.json().get('status') == 'timeout':
                    timestamp = response.json().get('timestamp_to_request')
                    params = {'timestamp': timestamp}
            except Exception as e:
                logger.error(e)
        sleep(1)


if __name__ == '__main__':
    request_check()
