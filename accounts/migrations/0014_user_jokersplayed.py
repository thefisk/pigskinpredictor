# Generated by Django 2.2.19 on 2022-05-26 10:33

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_user_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='JokersPlayed',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]