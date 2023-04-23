from django_celery_beat.models import MINUTES

from monitoring.models import TwitterMonitoring
from scheduling.models import TaskScheduler
from monitoring.tasks import monitor_user


def schedule_monitoring_task(monitoring_id):
    monitoring = TwitterMonitoring.objects.get(pk=monitoring_id)
    task_name = f"monitor_user_{monitoring_id}"

    # Terminate and delete the old task if it exists
    if monitoring.task:
        monitoring.task.terminate()
        monitoring.task.delete()

    # Create and schedule a new task
    new_task = TaskScheduler.schedule_every(
        task_name=task_name,
        task=monitor_user.name,
        period=MINUTES,
        every=monitoring.check_rate,
        args=[monitoring_id],
    )
    print(new_task)

    return new_task