## TaskScheduler
The TaskScheduler class is a utility for scheduling tasks to run at regular intervals or at specific clocked times. It uses the Django PeriodicTask model to manage the scheduling of tasks.

### Installation

To use the TaskScheduler class, you will need to have Django installed in your project.

### Usage
Scheduling an interval task
To schedule a task to run at regular intervals, use the schedule_every method. This method takes the following parameters:

- `task_name`: A unique name for the task.
- `task`: The task to run.
- `period`: The period of the interval (DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS).
- `every`: The number of periods between task runs.
- `args (optional)`: Arguments to pass to the task function.
- `kwargs (optional)`: Keyword arguments to pass to the task function.

Here's an example of how to use the schedule_every method:

```
from django.utils import timezone
from .models import TaskScheduler

def my_task():
    print("This is my task")

TaskScheduler.schedule_every(
    task_name="my_task",
    task="path.to.my_task",
    period=TaskScheduler.MINUTES,
    every=5,
    args=[1, 2, 3],
    kwargs={"foo": "bar"},
)
```
This will schedule the `my_task` function to run every 5 minutes with the arguments `[1, 2, 3]` and keyword arguments `{"foo": "bar"}`.

Scheduling a clocked task
To schedule a task to run at a specific time, use the schedule_clocked method. This method takes the following parameters:

* `task_name`: A unique name for the task.
* `task`: The task to run.
* `clocked_time`: The time at which the task should run.
* `args (optional)`: Arguments to pass to the task function.
* `kwargs (optional)`: Keyword arguments to pass to the task function.

Here's an example of how to use the schedule_clocked method:

```
from django.utils import timezone
from .models import TaskScheduler

def my_task():
    print("This is my task")

scheduled_time = timezone.now() + timedelta(minutes=5)

TaskScheduler.schedule_clocked(
    task_name="my_task",
    task="path.to.my_task",
    clocked_time=scheduled_time,
    args=[1, 2, 3],
    kwargs={"foo": "bar"},
)
```
This will schedule the `my_task` function to run at the specified time with the arguments `[1, 2, 3]` and keyword arguments `{"foo": "bar"}`.

### Starting and stopping tasks

To start or stop a scheduled task, use the start or stop method on the TaskScheduler instance:

```
task_scheduler = TaskScheduler.objects.get(pk=1)
task_scheduler.start()  # starts the task
task_scheduler.stop()  # stops the task
```

### Terminating a task
To terminate a scheduled task and remove it from the PeriodicTask model, use the terminate method on the TaskScheduler instance:

```
task_scheduler = TaskScheduler.objects.get(pk=1)
task_scheduler.terminate()  # stops and deletes the task
```