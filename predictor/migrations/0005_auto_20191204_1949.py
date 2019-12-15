# Generated by Django 2.2.7 on 2019-12-04 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0004_auto_20191204_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoresalltime',
            name='AllTimeBankerAverage',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='scoresalltime',
            name='AllTimeAverage',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True),
        ),
    ]