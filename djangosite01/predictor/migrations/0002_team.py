# Generated by Django 2.1.7 on 2019-03-18 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ShortName', models.CharField(max_length=4)),
                ('Town', models.CharField(max_length=20)),
                ('Nickname', models.CharField(max_length=20)),
            ],
        ),
    ]
