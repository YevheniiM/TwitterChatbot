import logging

from telegram_app import bot

logger = logging.getLogger()


def send_message(group_id, text):
    print(f"Sending to: {group_id}")
    try:
        res = bot.send_message(int(group_id), text=text)
        print(f"Sent message to {group_id}: {res}")
    except Exception as ex:
        print(str(ex))
