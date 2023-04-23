# Generated by Django 4.1.8 on 2023-04-23 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0001_initial'),
        ('monitoring', '0008_alter_twittermonitoring_telegram_channel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twittermonitoring',
            name='task',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scheduling.taskscheduler'),
        ),
    ]