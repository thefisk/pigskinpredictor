# Generated by Django 2.2.19 on 2021-08-23 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0024_livegame_kickoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='livegame',
            name='TeamIndex',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
