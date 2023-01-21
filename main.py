import os
from time import sleep

import requests
import telegram
from loguru import logger
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telegram.Bot(os.getenv('BOT_TOKEN'))


def get_chat_id():
    try:
        chat_id = bot.get_updates()[-1].message.chat_id
    except Exception as e:
        logger.error(e)
        chat_id = None
    return chat_id


def request_check():
    chat_id = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36',
        'Authorization': os.getenv('DEV_MAN_TOKEN')
    }
    url = 'https://dvmn.org/api/long_polling/'
    params = None
    while True:
        if not chat_id:
            chat_id = get_chat_id()
        else:
            try:
                if params:
                    response = requests.get(
                        url=url, headers=headers, params=params
                    )
                else:
                    response = requests.get(url=url, headers=headers)
                response.raise_for_status()
                if response.json().get('status') == 'found':
                    attempt = response.json().get('new_attempts')[0]
                    title = attempt.get('lesson_title')
                    lesson_link = attempt.get('lesson_url')
                    if attempt.get('is_negative'):
                        teacher_result = 'К сожалению, ' \
                                         'в работе нашлись ошибки.'
                    else:
                        teacher_result = 'Преподавателю всё понравилось, ' \
                                         'можно приступать к следующему уроку!'
                    message_text = f'У вас проверили работу "{title}".\n' \
                                   f'{teacher_result}\n' \
                                   f'{lesson_link}'
                    bot.send_message(
                        chat_id=chat_id, text=message_text
                    )
                    params = None
                elif response.json().get('status') == 'timeout':
                    timestamp = response.json().get('timestamp_to_request')
                    params = {'timestamp': timestamp}
            except Exception as e:
                logger.error(e)
        sleep(1)


if __name__ == '__main__':
    request_check()
