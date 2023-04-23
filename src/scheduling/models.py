import json

from django.db import models
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    DAYS,
    HOURS,
    MINUTES,
    SECONDS,
    MICROSECONDS,
    ClockedSchedule,
)


class TaskScheduler(models.Model):
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE)

    @staticmethod
    def schedule_every(task_name, task, period, every, args=None, kwargs=None):
        permissible_periods = [DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS]

        if period not in permissible_periods or every < 0:
            raise Exception('Invalid period specified')

        task_name = "%s_%s" % (task_name, task)
        interval_schedule, _ = IntervalSchedule.objects.get_or_create(
            period=period, every=every
        )
        task = PeriodicTask(name=task_name, task=task, interval=interval_schedule)
        if args:
            task.args = json.dumps(args)
        if kwargs:
            task.kwargs = json.dumps(kwargs)
        task.save()
        return TaskScheduler.objects.create(periodic_task=task)

    @staticmethod
    def schedule_clocked(task_name, task, clocked_time, args=None, kwargs=None):
        task_name = "%s_%s" % (task_name, task)
        clocked_schedule, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=clocked_time
        )
        task = PeriodicTask(
            name=task_name, task=task, clocked=clocked_schedule, one_off=True
        )
        if args:
            task.args = json.dumps(args)
        if kwargs:
            task.kwargs = json.dumps(kwargs)
        task.save()
        return TaskScheduler.objects.create(periodic_task=task)

    def stop(self):
        """stops the task"""
        task = self.periodic_task
        task.enabled = False
        task.save()

    def start(self):
        """starts the task"""
        task = self.periodic_task
        task.enabled = True
        task.save()

    def terminate(self):
        """terminates the task"""
        print('> terminating the task', flush=True)
        self.stop()
        task = self.periodic_task
        self.delete()
        task.delete()
