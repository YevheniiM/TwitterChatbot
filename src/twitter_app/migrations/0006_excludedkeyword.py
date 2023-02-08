# Generated by Django 4.1.6 on 2023-02-08 21:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_app', '0005_twitteruser_channel_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcludedKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=127)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excluded_keywords', to='twitter_app.twitteruser')),
            ],
        ),
    ]
