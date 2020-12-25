# Generated by Django 3.1.1 on 2020-12-25 05:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_auto_20201225_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 25, 5, 49, 53, 410796, tzinfo=utc), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 25, 5, 49, 53, 410796, tzinfo=utc), verbose_name='生成时间'),
        ),
    ]
