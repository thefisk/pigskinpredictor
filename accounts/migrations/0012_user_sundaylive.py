# Generated by Django 2.2.19 on 2021-09-13 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20210910_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='SundayLive',
            field=models.BooleanField(default=True, verbose_name='Show Sunday Live Scores'),
        ),
    ]