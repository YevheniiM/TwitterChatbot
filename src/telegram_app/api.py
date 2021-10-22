import logging
import time

from telegram_app import bot

logger = logging.getLogger()


def send_message(group_id, text):
    print(f"Sending to: {group_id}")
    for i in range(5):
        try:
            res = bot.send_message(int(group_id), text=text)
            print(f"Sent message to {group_id}: {res}, {text}")
            break
        except Exception as ex:
            print(str(ex))
            time.sleep(0.5)
