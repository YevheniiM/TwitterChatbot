import logging
import os
import re
import time

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

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def find_whole_word(word):
    word = '\\' + word if word.startswith('$') else word
    return re.compile(r'({0})'.format(word), flags=re.IGNORECASE).search


class KeywordManager:
    def __init__(self, message):
        self.message = message
        self.user = self._get_user(message)
        if not self.user:
            raise Exception("Couldn't find a user")
        self.include_replies = self.user.include_replies
        self.include_retweets = self.user.include_retweets

    @staticmethod
    def _get_user(message):
        try:
            user_id = message.get('user', {}).get('id', None)
            if user_id:
                user = TwitterUser.objects.get(user_id=user_id)
                print(f"Found user: {user}, keywords: {user.keywords}")
                return user
            logger.error(f"User is not found, message: {message}")
        except models.ObjectDoesNotExist as ex:
            logger.warning(ex)

    def _send_message(self, keywords, tweet_type):
        url = f"https://twitter.com/{self.user.username}/status/{self.message.get('id_str', '')}"
        if keywords:
            message = f"Username: {self.user.username} [{self.user.channel_name}]\n" \
                      f"Keywords: {', '.join(keywords)}\n" \
                      f"Type of tweet: {tweet_type}\n" \
                      f"Full url: {url}"
            send_message(self.user.chat_id, message)
        else:
            print(f"No keywords were found in {self.message}")

    def _process_retweets(self):
        if self.message.get('retweeted_status', False):
            if self.message.get('retweeted_status').get('truncated', False):
                text = self.message.get('retweeted_status').get('extended_tweet', {}).get('full_text', '')
            else:
                text = self.message.get('retweeted_status').get('text')

            print(f"*** retweet ***\n{text}")

            keywords = self._get_keywords(text)
            print(f"Found {len(keywords)} keywords")

            self._send_message(keywords, tweet_type="retweet")
            return True

        if self.message.get('quoted_status', False):
            if self.message.get('quoted_status').get('truncated', False):
                quoted_text = self.message.get('quoted_status').get('extended_tweet', {}).get('full_text', '')
            else:
                quoted_text = self.message.get('quoted_status').get('text', '')
            quote = self.message.get('text', '')

            print(f"*** quote ***\n{quote}\n{quoted_text}")

            keywords = []
            keywords.extend(self._get_keywords(quote))
            keywords.extend(self._get_keywords(quoted_text))

            print(f"Found {len(keywords)} keywords")

            self._send_message(keywords, tweet_type="quote")
            return True

        return False

    def _process_replies(self):
        if self.message.get('in_reply_to_status_id', False):
            tweet = api.get_status(self.message.get('in_reply_to_status_id'))._json
            text = tweet.get('text', '')
            reply = self.message.get('text')

            print(f"*** reply ***\nReply: {reply}\nText: {text}")

            keywords = []
            keywords.extend(self._get_keywords(text))
            keywords.extend(self._get_keywords(reply))

            print(f"Found {len(keywords)} keywords")

            self._send_message(keywords, tweet_type="reply")
            return True
        return False

    def _process_tweets(self):
        if not (self.message.get('quoted_status', False) or self.message.get('retweeted_status', False)
                or self.message.get('in_reply_to_status_id', False)):
            if self.message.get('truncated', False):
                text = self.message.get('extended_tweet', {}).get('full_text', '')
            else:
                text = self.message.get('text', '')

            keywords = self._get_keywords(text)
            self._send_message(keywords, tweet_type="tweet")
            return True
        return False

    def process(self):
        if self.include_replies and self.include_retweets:
            retweets_processed = self._process_retweets()
            if not retweets_processed:
                self._process_replies()
        elif self.include_replies:
            self._process_replies()
        elif self.include_retweets:
            self._process_retweets()
        self._process_tweets()

    def _get_keywords(self, text):
        keywords = self.user.keywords.all()
        found_keywords = []

        for keyword in keywords:
            if find_whole_word(keyword.keyword)(text) is not None:
                found_keywords.append(keyword.keyword)

        logger.info(f"Found keywords: {found_keywords} for user: {self.user.username} [{self.user.user_id}]")
        return found_keywords


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status, ):
        message_obj = status._json
        try:
            manager = KeywordManager(message_obj)
        except Exception as ex:
            print(ex)
            print("Status was not processed (error during the KeywordManager creation")
            return

        manager.process()

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
