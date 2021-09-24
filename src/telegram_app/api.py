from pprint import pprint

from telegram_app import bot


def send_message(group_id, text):
    print(group_id)
    pprint(bot.send_message(int(group_id), text=text))
