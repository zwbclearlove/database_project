# Generated by Django 3.1.4 on 2020-12-20 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_footprint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default='user\\images\\default_avatar.png', null=True, upload_to='user/images', verbose_name='头像'),
        ),
    ]
