# Generated by Django 2.2.19 on 2021-04-15 13:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_user_jokerused'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Positions',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
