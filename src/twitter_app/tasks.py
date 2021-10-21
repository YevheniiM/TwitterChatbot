import logging
import re

import tweepy
from celery import shared_task
from django.db import models

from telegram_app.api import send_message
from twitter_app.models import TwitterUser

logger = logging.getLogger("celery_twitter_app")




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
                user = TwitterUser.objects.get(user_id=str(user_id))
                print(f"Found user: {user}, keywords: {user.keywords}")
                return user
            print(message)
            logger.error(f"User is not found, message: {message}")
        except models.ObjectDoesNotExist as ex:
            print(message)
            print(ex)

    @staticmethod
    def find_whole_word(word):
        word = '\\' + word if word.startswith('$') else word
        return re.compile(r'({0})'.format(word), flags=re.IGNORECASE).search

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
            if self.find_whole_word(keyword.keyword)(text) is not None:
                found_keywords.append(keyword.keyword)

        logger.info(f"Found keywords: {found_keywords} for user: {self.user.username} [{self.user.user_id}]")
        return found_keywords


@shared_task
def parse_tweet(tweet):
    try:
        print("Starting parsing the tweeter task...")
        manager = KeywordManager(tweet)
        manager.process()
    except Exception as ex:
        print(ex)
        print("Status was not processed (error during the KeywordManager creation)")
        return
