# Generated by Django 2.1.1 on 2019-04-23 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20190422_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staytime',
            name='created_at',
            field=models.DateField(verbose_name='创建于'),
        ),
    ]
