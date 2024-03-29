# Generated by Django 4.1.8 on 2023-04-23 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_alter_twittermonitoring_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('twitter_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('twitter_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='twittermonitoring',
            name='followers',
            field=models.ManyToManyField(related_name='monitorings_followers', to='monitoring.followers'),
        ),
        migrations.AddField(
            model_name='twittermonitoring',
            name='friends',
            field=models.ManyToManyField(related_name='monitorings_friends', to='monitoring.friends'),
        ),
    ]
