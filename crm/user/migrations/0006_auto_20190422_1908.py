# Generated by Django 2.1.1 on 2019-04-22 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20190422_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservisit',
            name='created_at',
            field=models.DateField(unique_for_date=True, verbose_name='创建于'),
        ),
    ]
