# Generated by Django 2.1.1 on 2019-04-28 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20190428_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='last_active_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='活跃时间'),
        ),
    ]
