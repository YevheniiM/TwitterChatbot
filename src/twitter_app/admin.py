import logging

import tweepy
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import display

from twitter_app.models import TwitterUser, Keyword

logger = logging.getLogger()


class KeywordInline(admin.TabularInline):
    model = Keyword
    verbose_name_plural = "Keyword"
    max_num = 10


class TwitterUserAdmin(admin.ModelAdmin):
    inlines = [KeywordInline]
    model = TwitterUser

    list_display = ('username', 'get_keywords', 'channel_name')

    def save_model(self, request, obj, form, change):
        auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
        auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        if 'username' in form.changed_data:
            user = api.get_user(screen_name=form.cleaned_data.get('username'))
            obj.user_id = user.id
            logger.info(f"Saved user with username: {obj.username}, id: {obj.user_id}")
        super().save_model(request, obj, form, change)

    @display(description='Keywords  ')
    def get_keywords(self, obj):
        return list(obj.keywords.all())


admin.site.register(TwitterUser, TwitterUserAdmin)
admin.site.register(Keyword)
