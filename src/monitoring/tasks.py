import logging
from urllib.parse import quote

import tweepy
from celery import shared_task
from django.conf import settings

from monitoring.models import TwitterMonitoring, Friends
from telegram_app.api import send_message

logger = logging.getLogger("celery_twitter_app")

auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


@shared_task
def monitor_user(monitoring_id):
    monitoring = TwitterMonitoring.objects.get(pk=monitoring_id)
    twitter_handle = monitoring.twitter_handle

    try:
        # Get user's friends (accounts the user follows)
        friends = api.get_friend_ids(screen_name=twitter_handle, count=5000)

        print(f'Friends: {friends}')

        # Update friends
        current_friends = set(monitoring.friends.values_list('twitter_id', flat=True))
        new_friends = set(friends) - current_friends
        lost_friends = current_friends - set(friends)

        if current_friends:
            print(f"New friends: {new_friends}")
            print(f"Lost friends: {lost_friends}")

        for friend_id in new_friends:
            friend, _ = Friends.objects.get_or_create(twitter_id=friend_id)

            if current_friends:
                new_friend = api.get_user(user_id=friend_id)
                target_profile_url = f"https://twitter.com/{quote(twitter_handle)}"
                new_friend_profile_url = f"https://twitter.com/{quote(new_friend.screen_name)}"
                message = f"{twitter_handle} ({target_profile_url}) started following {new_friend.screen_name} ({new_friend_profile_url})"
                send_message(monitoring.telegram_channel, message)

            monitoring.friends.add(friend)

        for friend_id in lost_friends:
            friend = Friends.objects.get(twitter_id=friend_id)
            monitoring.friends.remove(friend)

    except Exception as e:
        print(f"Error monitoring user '{twitter_handle}': {e}")
