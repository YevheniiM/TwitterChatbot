from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TwitterMonitoring
from .schedule_monitoring import schedule_monitoring_task


@receiver(post_save, sender=TwitterMonitoring)
def schedule_task(sender, instance, created, **kwargs):
    if created:
        task = schedule_monitoring_task(instance.pk)
        TwitterMonitoring.objects.filter(pk=instance.pk).update(task=task)
    else:
        instance.task.terminate()
        task = schedule_monitoring_task(instance.pk)
        TwitterMonitoring.objects.filter(pk=instance.pk).update(task=task)
