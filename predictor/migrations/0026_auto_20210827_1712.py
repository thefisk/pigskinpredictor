# Generated by Django 2.2.19 on 2021-08-27 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0025_livegame_teamindex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livegame',
            name='State',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
