# Generated by Django 2.1.1 on 2019-05-22 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_userinfo_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDailyData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(verbose_name='创建于')),
                ('store_times', models.IntegerField(default=0, verbose_name='参观小店次数')),
                ('sample_times', models.IntegerField(default=0, verbose_name='参观样板房次数')),
                ('access_times', models.IntegerField(default=0, verbose_name='到访次数')),
                ('total_time', models.IntegerField(default=0, verbose_name='总秒数')),
                ('store_time', models.IntegerField(default=0, verbose_name='参观小店秒数')),
                ('sample_time', models.IntegerField(default=0, verbose_name='参观样板房秒数')),
                ('big_room_time', models.IntegerField(default=0, verbose_name='大厅停留秒数')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.BaseUser', verbose_name='用户')),
            ],
        ),
    ]