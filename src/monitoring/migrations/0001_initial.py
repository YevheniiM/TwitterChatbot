# Generated by Django 4.1.8 on 2023-04-16 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterMonitoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_handle', models.CharField(max_length=255)),
                ('check_rate', models.IntegerField(default=10)),
            ],
        ),
    ]