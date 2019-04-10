# Generated by Django 2.1.1 on 2019-04-04 11:19

from django.db import migrations, models

import crm


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20190404_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='extra_data',
            field=models.TextField(default={}, verbose_name='额外参数'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='msg_last_at',
            field=models.DateTimeField(default=crm.user.models.before_day, verbose_name='上次读取消息时间'),
        ),
    ]
