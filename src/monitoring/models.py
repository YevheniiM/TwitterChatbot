from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from scheduling.models import TaskScheduler


class Friends(models.Model):
    twitter_id = models.CharField(primary_key=True, max_length=255)


class TwitterMonitoring(models.Model):
    twitter_handle = models.CharField(max_length=255)
    check_rate = models.IntegerField(default=10)
    task = models.OneToOneField(TaskScheduler, on_delete=models.SET_NULL, null=True, blank=True)
    friends = models.ManyToManyField(Friends, related_name='monitorings_friends', blank=True)
    telegram_channel = models.CharField(max_length=255,
        null=True,
        blank=True,
        help_text='It is an integer value field that represents the id of the telegram channel.\n'
                  'In order to obtain this id, you should create a public channel (can be changed later), copy'
                  ' the joining link and paste it to this bot: https://t.me/username_to_id_bot. Then just copy'
                  ' an id from the output and paste it here'
    )

    def delete(self, *args, **kwargs):
        print('> deleting with', self.task, flush=True)
        # Revoke the Celery task
        if self.task:
            self.task.terminate()

        # Call the original delete method
        super(TwitterMonitoring, self).delete(*args, **kwargs)

    def validate_check_rate(self):
        total_checks_per_15_min = 15
        total_minutes_per_15_min = 15

        all_monitored_users = TwitterMonitoring.objects.exclude(pk=self.pk)
        all_monitored_users = list(all_monitored_users.values_list('check_rate', flat=True)) + [self.check_rate]

        checks_per_15_min = sum([total_minutes_per_15_min / rate for rate in all_monitored_users])

        if checks_per_15_min > total_checks_per_15_min:
            raise ValidationError(
                "The combined check rates exceed the Twitter API rate limit. Please choose a slower check rate.")

    def clean(self):
        self.validate_check_rate()
