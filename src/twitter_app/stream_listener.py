import logging
import sys
import time
from threading import Thread

import celery
import tweepy
from django.conf import settings
from urllib3.exceptions import ProtocolError

from tasks import app
from twitter_app.models import TwitterUser
from twitter_app.tasks import parse_tweet

logger = logging.getLogger("stream_listener")

auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        self.running = True
        super().__init__()

    def on_status(self, status):
        print("Got the new tweet...")
        celery.current_app.send_task("twitter_app.tasks.parse_tweet", args=[status._json])

        if not self.running:
            print("Raising exception in a listening thread")
            raise Exception("Users has been changed, restarting the app")

    def on_error(self, status_code):
        logger.error(f"on_error got {status_code} status code")
        if status_code == 420:
            return False
        return True


class ThreadedWrapper:
    def __init__(self, stream: tweepy.Stream):
        self.running = True
        self.stream = stream

    def threaded_function(self, initial_ids):
        while self.running:
            try:
                self.stream.filter(initial_ids, is_async=False, stall_warnings=True)
            except (ProtocolError, AttributeError) as ex:
                print(f"[ERROR]: protocol error: {ex}")
                continue
        print("Exiting the threaded_function....")

    def disconnect(self):
        self.running = False
        self.stream.disconnect()


def main():
    print("Starting stream_listener...")

    while True:
        try:
            my_stream_listener = MyStreamListener()
            my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)

            while True:
                initial_ids = TwitterUser.objects.values_list("user_id", flat=True)
                if not initial_ids:
                    time.sleep(0.1)
                    continue

                print(f"Starting filtering on {initial_ids}...")
                wrapper = ThreadedWrapper(my_stream)
                thread = Thread(target=wrapper.threaded_function, args=(initial_ids,))
                thread.start()

                while True:
                    ids = TwitterUser.objects.values_list("user_id", flat=True)

                    if set(initial_ids) != set(ids):
                        print(f"New user [{set(ids) - set(initial_ids)}] was added")
                        print("Disconnecting the stream...")
                        wrapper.disconnect()
                        thread.join()
                        print("Stream joined! Restarting...")
                        break

                    time.sleep(0.5)
        except Exception as ex:
            print("Exception in the most outer while loop")
            print(ex)
            time.sleep(1)


main()
