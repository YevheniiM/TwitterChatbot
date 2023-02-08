import logging
import re

import requests
import tweepy
from celery import shared_task
from django.conf import settings
from django.db import models

from telegram_app.api import send_message
from twitter_app.models import TwitterUser

logger = logging.getLogger("celery_twitter_app")

auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def check_tweet_type(tweet_data: dict):
    if (
            tweet_data.get('referenced_tweets') and
            tweet_data.get('referenced_tweets')[0].get('type')
    ):
        return tweet_data.get('referenced_tweets')[0].get('type')


# noinspection PyProtectedMember
class KeywordManager:
    def __init__(self, tweet_data: dict):
        self.tweet_data = tweet_data
        self.user = self._get_user(tweet_data)
        if not self.user:
            raise Exception(f"Couldn't find a user, message: {self.tweet_data.get('text', '')}")
        self.include_replies = self.user.include_replies
        self.include_retweets = self.user.include_retweets

    @staticmethod
    def _get_user(message):
        try:
            user_id = message.get('author_id')
            if user_id:
                user = TwitterUser.objects.get(user_id=str(user_id))
                print(f"Found user: {user}")
                return user
            print(f"User is not found, message: {message.get('text', '')}")
        except models.ObjectDoesNotExist as ex:
            print(ex)

    @staticmethod
    def find_whole_word(word):
        word = '\\' + word if word.startswith('$') else word
        return re.compile(r'({0})'.format(word), flags=re.IGNORECASE).search

    def _send_message(self, keywords, tweet_type):
        url = f"https://twitter.com/{self.user.username}/status/{self.tweet_data.get('id', '')}"
        if keywords:
            message = f"Username: {self.user.username} [{self.user.channel_name}]\n" \
                      f"Keywords: {', '.join(keywords)}\n" \
                      f"Type of tweet: {tweet_type}\n" \
                      f"Full url: {url}"
            send_message(self.user.chat_id, message)
        else:
            print(f"No keywords were found in {self.tweet_data.get('text', '')}")

    def _process_retweets(self):
        if check_tweet_type(self.tweet_data) == 'retweeted':
            tweet_id = self.tweet_data.get('referenced_tweets')[0].get('id')
            tweet = api.get_status(tweet_id, tweet_mode="extended")._json
            original_tweet = tweet.get('full_text')

            print(f"*** retweet ***\n{original_tweet}")

            keywords = self._get_keywords(original_tweet)
            print(f"Found {len(keywords)} keywords")

            self._send_message(keywords, tweet_type="retweet")
            return True

        if check_tweet_type(self.tweet_data) == 'quoted':
            tweet_id = self.tweet_data.get('referenced_tweets')[0].get('id')
            quoted_text = api.get_status(tweet_id, tweet_mode="extended")._json.get('full_text')
            quote = self.tweet_data.get('text', '')

            print(f"*** quote ***\n{quote}\n{quoted_text}")

            keywords = []
            keywords.extend(self._get_keywords(quote))
            keywords.extend(self._get_keywords(quoted_text))

            print(f"Found {len(keywords)} keywords")

            self._send_message(keywords, tweet_type="quote")
            return True

        return False

    def _process_replies(self):
        if check_tweet_type(self.tweet_data) == 'replied_to':
            reply = self.tweet_data.get('text')
            if self.tweet_data.get('referenced_tweets'):
                original = api.get_status(
                    self.tweet_data.get('referenced_tweets')[0].get('id'),
                    tweet_mode="extended"
                )
                original_text = original._json.get('full_text')

                print(f"*** reply ***\nReply: {reply}\nText: {original_text}")

                keywords = []
                keywords.extend(self._get_keywords(original_text))
                keywords.extend(self._get_keywords(reply))

                print(f"Found {len(keywords)} keywords")

                self._send_message(keywords, tweet_type="reply")
                return True
        return False

    def _process_tweets(self):
        if not check_tweet_type(self.tweet_data):
            text = self.tweet_data.get('text', '')
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
        text = self._replace_urls(text)
        keywords = self.user.keywords.all()
        excluded_keywords = self.user.excluded_keywords.all()
        found_keywords = []

        for excluded in excluded_keywords:
            if self.find_whole_word(excluded.keyword)(text) is not None:
                logger.info(f"Excluding tweet, because found excluded keyword: {excluded.keyword}")
                return []

        for keyword in keywords:
            if self.find_whole_word(keyword.keyword)(text) is not None:
                found_keywords.append(keyword.keyword)

        logger.info(f"Found keywords: {found_keywords} for user: {self.user.username} [{self.user.user_id}]")
        return found_keywords

    @staticmethod
    def _replace_urls(text):
        url_regex = re.compile(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)")
        urls = re.findall(url_regex, text)

        for url in urls:
            expanded_url = requests.head(url, allow_redirects=True).url
            text = text.replace(url, expanded_url)

        return text

@shared_task
def parse_tweet(tweet):
    try:
        print("Starting parsing the tweeter task...")
        manager = KeywordManager(tweet)
        manager.process()
    except Exception as ex:
        print(ex)
        print("Status was not processed (error during the KeywordManager creation)")
