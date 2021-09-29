import logging

from telegram_app import bot

logger = logging.getLogger()


def send_message(group_id, text):
    logger.info(f"Sending to: {group_id}")
    try:
        res = bot.send_message(int(group_id), text=text)
        logger.info(f"Sent message to {group_id}: {res}")
    except Exception as ex:
        logger.error(str(ex))
