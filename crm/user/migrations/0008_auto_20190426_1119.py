# Generated by Django 2.1.1 on 2019-04-26 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20190423_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservisit',
            name='all_access_total',
            field=models.IntegerField(default=0, verbose_name='来访人次'),
        ),
        migrations.AddField(
            model_name='uservisit',
            name='all_micro_store_total',
            field=models.IntegerField(default=0, verbose_name='小店参数人次'),
        ),
        migrations.AddField(
            model_name='uservisit',
            name='all_sample_room_total',
            field=models.IntegerField(default=0, verbose_name='样板房参观人次'),
        ),
    ]
