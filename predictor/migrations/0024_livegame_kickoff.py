# Generated by Django 2.2.19 on 2021-08-23 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0023_livegame_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='livegame',
            name='KickOff',
            field=models.IntegerField(default=1700),
            preserve_default=False,
        ),
    ]
