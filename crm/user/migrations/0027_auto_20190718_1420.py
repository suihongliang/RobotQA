# Generated by Django 2.1.1 on 2019-07-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_auto_20190716_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='live_space',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='工作区域'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='work_space',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='工作区域'),
        ),
    ]