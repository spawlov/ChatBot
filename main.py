import os

import requests
import telegram
from dotenv import load_dotenv, find_dotenv
from loguru import logger

logger.remove()


def send_message(response_raw, chat_id):
    """Sending message to user"""
    attempt = response_raw.get('new_attempts')[0]
    title = attempt.get('lesson_title')
    lesson_link = attempt.get('lesson_url')
    logger.info(response_raw)

    if attempt.get('is_negative'):
        teacher_result = 'К сожалению, в работе нашлись ошибки.'
    else:
        teacher_result = '''
        Преподавателю всё понравилось, можно приступать к следующему уроку!'''

    message_text = f'''
    У вас проверили работу "{title}".\n{teacher_result}\n{lesson_link}'''

    bot.send_message(chat_id=chat_id, text=message_text)


def get_lesson_status():
    """Check lesson status"""
    chat_id = params = None
    url = 'https://dvmn.org/api/long_polling/'
    while True:
        if not chat_id:
            chat_id = bot.get_updates()[-1].message.chat_id
            logger.debug(f'Chat ID = {chat_id}')

        if chat_id not in allowed_chats:
            logger.error(f'Chat ID: {chat_id} is not allowed')
            chat_id = allowed_chats[0]
            logger.debug(f'Chat ID = {chat_id}')

        try:
            response = requests.get(url=url, headers=headers, params=params)
            response.raise_for_status()
            response_raw = response.json()
            if 'error' in response_raw:
                raise requests.exceptions.HTTPError(response_raw['error'])
        except requests.exceptions.ReadTimeout as e:
            logger.error(e)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        else:
            logger.debug(response_raw['request_query'])
            if response_raw['status'] == 'found':
                send_message(response_raw, chat_id)
                params = {'timestamp': response_raw['last_attempt_timestamp']}
            elif response_raw['status'] == 'timeout':
                params = {'timestamp': response_raw['timestamp_to_request']}


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    bot = telegram.Bot(os.getenv('BOT_TOKEN'))
    headers = {'Authorization': os.getenv('DEVMAN_TOKEN')}
    allowed_chats = list(map(int, os.getenv('ALLOWED_CHAT_ID').split(',')))
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
    get_lesson_status()
