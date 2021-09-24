from django.db import models


class TwitterUser(models.Model):
    username = models.CharField(max_length=255, null=False, blank=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    chat_id = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.username


class Keyword(models.Model):
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=127, null=False, blank=False)
