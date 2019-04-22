# Generated by Django 2.1.1 on 2019-04-22 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190418_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='StayTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_seconds', models.IntegerField(default=0, verbose_name='样板房逗留时间')),
                ('micro_seconds', models.IntegerField(default=0, verbose_name='微店逗留时间')),
                ('big_room_seconds', models.IntegerField(default=0, verbose_name='大厅逗留时间')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='创建于')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.BaseUser', verbose_name='用户')),
            ],
            options={
                'verbose_name': '大厅逗留时间',
                'verbose_name_plural': '大厅逗留时间',
            },
        ),
    ]
