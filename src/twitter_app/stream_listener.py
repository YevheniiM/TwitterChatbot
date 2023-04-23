import logging
import time
from threading import Thread

import requests.exceptions
import tweepy
from django.conf import settings

from tasks import app
from twitter_app.models import TwitterUser

logger = logging.getLogger("stream_listener")

auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token, **kwargs):
        self.running = True
        super().__init__(bearer_token, **kwargs)

    def on_tweet(self, tweet):
        print(f"Got the new tweet: {tweet}\n{tweet.data}\n")
        print(f"Extended:\n")
        app.send_task("twitter_app.tasks.parse_tweet", args=[tweet.data])

        if not self.running:
            print("Raising exception in a listening thread")
            raise Exception("Users has been changed, restarting the app")

    def on_errors(self, errors):
        logger.error(f"on_error got {errors}")
        return True

class ThreadedWrapper:
    def __init__(self, stream: tweepy.StreamingClient):
        self.running = True
        self.stream = stream

    def threaded_function(self, initial_ids):
        rule = ""
        for i, id_ in enumerate(initial_ids):
            if i == 0:
                rule += f"from: {id_}"
            else:
                rule += f" OR from: {id_}"

        rules = self.stream.get_rules().data
        if rules:
            rules_ids = [r.id for r in rules]
            if len(rules_ids):
                print(self.stream.delete_rules(rules_ids))

        print(self.stream.add_rules(tweepy.StreamRule(rule)))

        print('Starting filtering the streem...')
        self.stream.filter(expansions=[
            'author_id',
            'referenced_tweets.id',
            'in_reply_to_user_id',
            'entities.mentions.username',
            'referenced_tweets.id.author_id',
        ])

    def disconnect(self):
        self.running = False
        self.stream.disconnect()


def connect_to_twitter_api(retries=5, backoff_factor=2):
    for retry_attempt in range(retries):
        try:
            auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
            auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)

        except requests.exceptions.ConnectionError as e:
            if retry_attempt == retries - 1:
                print("Connection error: reached maximum retries")
                raise e

            sleep_time = backoff_factor * (2 ** retry_attempt)
            print(f"Connection error: {e}. Retrying in {sleep_time} seconds.")
            time.sleep(sleep_time)
        else:
            break


def main():
    print("Starting stream_listener...")

    while True:
        try:
            my_stream = MyStreamListener(settings.BEARER_TOKEN)

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
        except requests.exceptions.ConnectionError as ex:
            print("ConnectionError in the most outer while loop")
            print(ex)
            connect_to_twitter_api()
        except Exception as ex:
            print("Exception in the most outer while loop")
            print(ex)
            time.sleep(1)


main()
