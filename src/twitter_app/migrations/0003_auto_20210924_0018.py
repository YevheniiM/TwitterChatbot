# Generated by Django 3.2.7 on 2021-09-24 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_app', '0002_rename_keywords_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteruser',
            name='chat_id',
            field=models.CharField(default='deafult', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='keyword',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='twitter_app.twitteruser'),
        ),
    ]
