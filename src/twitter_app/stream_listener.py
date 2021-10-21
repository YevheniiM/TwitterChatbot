import logging
import time

import celery
import tweepy
from django.conf import settings

from tasks import app
from twitter_app.models import TwitterUser
from twitter_app.tasks import parse_tweet

logger = logging.getLogger("stream_listener")

auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print("Got the new tweet...")
        print("Sending the task to the celery...")
        celery.current_app.send_task("twitter_app.tasks.parse_tweet", args=[status._json])

    def on_error(self, status_code):
        logger.error(f"on_error got {status_code} status code")
        if status_code == 420:
            return False
        return True


def main():
    print("Starting stream_listener...")

    while True:
        try:
            my_stream_listener = MyStreamListener()
            my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)

            while True:
                initial_ids = TwitterUser.objects.values_list("user_id", flat=True)
                if not initial_ids:
                    time.sleep(10)
                    continue

                print(f"Starting filtering on {initial_ids}...")
                my_stream.filter(initial_ids, is_async=True)

                while True:
                    ids = TwitterUser.objects.values_list("user_id", flat=True)

                    if set(initial_ids) != set(ids):
                        print(f"New user [{set(ids) - set(initial_ids)}] was added")
                        print("Disconnecting the stream...")
                        my_stream.disconnect()
                        break

                    time.sleep(10)
        except Exception as ex:
            print("Exception in the most outer while loop")
            print(ex)
            time.sleep(120)


main()
