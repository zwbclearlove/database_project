# Generated by Django 3.1.1 on 2020-12-05 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_favorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='FootPrint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='所属用户')),
                ('product_id', models.IntegerField(verbose_name='所属商品')),
                ('create_time', models.DateTimeField(verbose_name='访问时间')),
            ],
        ),
    ]
