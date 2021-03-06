# Generated by Django 2.2.7 on 2019-12-02 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0002_auto_20191112_1653'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['Town', 'Nickname']},
        ),
        migrations.AddField(
            model_name='prediction',
            name='PredSeason',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='BankerAverage',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='SeasonAverage',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='SeasonBest',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='SeasonCorrect',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='SeasonPercentage',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='scoresseason',
            name='SeasonWorst',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
