# Generated by Django 2.1.1 on 2019-03-27 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190326_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='gender',
            field=models.IntegerField(choices=[(1, '男'), (2, '女'), (0, '未知')], default=0, verbose_name='性别'),
        ),
    ]
