# Generated by Django 4.1.8 on 2023-04-23 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_app', '0006_excludedkeyword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitteruser',
            name='include_replies',
            field=models.BooleanField(default=True),
        ),
    ]