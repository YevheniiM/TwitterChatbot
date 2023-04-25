import logging
import time

from telegram_app import bot

logger = logging.getLogger()


def send_message(group_id, text, parse_mode=None, disable_web_page_preview=False):
    print(f"Sending to: {group_id}")
    for i in range(5):
        try:
            res = bot.send_message(chat_id=group_id,
                                   text=text,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview)
            print(f"Sent message to {group_id}: {res}, {text}")
            break
        except Exception as ex:
            print(str(ex))
            time.sleep(0.5)
