# Generated by Django 4.0.2 on 2022-02-22 00:22

import datetime
from django.db import migrations, models
import landbot.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_name', models.CharField(max_length=255, unique=True)),
                ('audience', models.IntegerField(validators=[landbot.validators.validate_greater_than_zero])),
                ('schedule', models.DateTimeField(default=datetime.datetime.now, validators=[landbot.validators.validate_one_hour_after_now])),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
            },
        ),
    ]
