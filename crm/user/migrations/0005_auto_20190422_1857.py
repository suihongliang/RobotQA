# Generated by Django 2.1.1 on 2019-04-22 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_uservisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservisit',
            name='access_total',
            field=models.IntegerField(default=0, verbose_name='来访人数'),
        ),
        migrations.AlterField(
            model_name='uservisit',
            name='micro_store_total',
            field=models.IntegerField(default=0, verbose_name='小店参数人数'),
        ),
        migrations.AlterField(
            model_name='uservisit',
            name='register_total',
            field=models.IntegerField(default=0, verbose_name='注册人数'),
        ),
        migrations.AlterField(
            model_name='uservisit',
            name='sample_room_total',
            field=models.IntegerField(default=0, verbose_name='样板房参观人数'),
        ),
    ]
