import logging
import os
import time
from pprint import pprint

import tweepy
from django.db import models

from telegram_app.api import send_message
from twitter_app.models import TwitterUser

logger = logging.getLogger("stream_listener")

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        message_obj = status._json
        user_id = message_obj.get('user', {}).get('id', None)
        message = message_obj.get('text', '')

        if not user_id or not message:
            logger.error(f"user_id: {user_id}, message: {message}")
            return

        try:
            user = TwitterUser.objects.get(user_id=user_id)
            keywords = user.keywords.all()
        except models.ObjectDoesNotExist as ex:
            logger.warning(ex)
            return

        found_keywords = [keyword.keyword for keyword in keywords if keyword.keyword in message]
        logger.info(f"Found keywords: {found_keywords} for user: {user.username} [{user.user_id}]")

        # if found_keywords:
        send_message(user.chat_id, message)

        pprint(status.text)

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            return False
        return True


def main():
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    my_stream_listener = MyStreamListener()
    my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)

    while True:
        initial_ids = TwitterUser.objects.values_list("user_id", flat=True)
        if not initial_ids:
            time.sleep(15)
            continue

        my_stream.filter(initial_ids, is_async=True)

        while True:
            ids = TwitterUser.objects.values_list("user_id", flat=True)

            if set(initial_ids) != set(ids):
                my_stream.disconnect()
                break

            time.sleep(15)


main()
