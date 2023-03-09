import os
from time import sleep

import requests
import telegram
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from notifiers.logging import NotificationHandler

logger.remove()


def main():
    load_dotenv(find_dotenv())
    bot = telegram.Bot(os.getenv('NOTIFIER_BOT_TOKEN'))
    tg_handler_params = {
        'token': os.getenv('LOGGER_BOT_TOKEN'),
        'chat_id': int(os.getenv('ALLOWED_CHAT_ID'))
    }
    tg_handler = NotificationHandler('telegram', defaults=tg_handler_params)
    headers = {'Authorization': os.getenv('DEVMAN_TOKEN')}
    chat_id = int(os.getenv('ALLOWED_CHAT_ID'))
    logger.add(
        'debug.log',
        format='{level}::{time}::{message}',
        level='DEBUG',
        rotation='0:00',
        compression='zip',
    )
    logger.add(
        'info.log',
        format='{level}::{time}::{message}',
        level='INFO',
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
    logger.add(tg_handler, level="INFO")
    get_lesson_status(chat_id, headers, bot)


def send_message(lesson_status, chat_id, bot):
    """Sending message to user"""
    attempt = lesson_status.get('new_attempts')[0]
    title = attempt.get('lesson_title')
    lesson_link = attempt.get('lesson_url')
    logger.info(lesson_status)

    if attempt.get('is_negative'):
        teacher_result = 'К сожалению, в работе нашлись ошибки.'
    else:
        teacher_result = f'''
        Преподавателю всё понравилось, можно приступать к следующему уроку!'''

    message_text = f'''
    У вас проверили работу "{title}".\n{teacher_result}\n{lesson_link}'''

    bot.send_message(chat_id=chat_id, text=message_text)


def get_lesson_status(chat_id, headers, bot):
    """Check lesson status"""
    params = None
    attempt_connect = 0
    logger.debug(f'Chat ID: {chat_id}')
    url = 'https://dvmn.org/api/long_polling/'
    while True:
        try:
            attempt_connect += 1
            response = requests.get(url=url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout as e:
            logger.error(e)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            logger.error(f'Pause: {60 * attempt_connect} sec.')
            sleep(60 * attempt_connect)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        else:
            attempt_connect = 0
            lesson_status = response.json()
            logger.debug(lesson_status['request_query'])
            if lesson_status['status'] == 'found':
                send_message(lesson_status, chat_id, bot)
                params = {'timestamp': lesson_status['last_attempt_timestamp']}
            elif lesson_status['status'] == 'timeout':
                params = {'timestamp': lesson_status['timestamp_to_request']}


if __name__ == '__main__':
    main()
