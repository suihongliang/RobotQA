# Generated by Django 2.1.1 on 2019-08-08 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EveryStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UserType', models.IntegerField(choices=[(0, '全部'), (1, '会员'), (2, '员工'), (3, '惯偷'), (4, '回头客'), (5, '普通顾客')], verbose_name='用户类型')),
                ('storeId', models.CharField(max_length=32, null=True, verbose_name='门店id')),
                ('dateTime', models.CharField(max_length=10, null=True, verbose_name='日期')),
                ('male_value', models.IntegerField(verbose_name='男性人数')),
                ('female_value', models.IntegerField(verbose_name='女性人数')),
                ('early_value', models.IntegerField(verbose_name='少年人数')),
                ('young_value', models.IntegerField(verbose_name='青年人数')),
                ('middle_value', models.IntegerField(verbose_name='中年人数')),
                ('old_value', models.IntegerField(verbose_name='老年人数')),
            ],
            options={
                'verbose_name_plural': '单日客群属性',
            },
        ),
        migrations.CreateModel(
            name='FaceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateTime', models.CharField(max_length=10, null=True, verbose_name='日期')),
                ('tenantId', models.CharField(max_length=64, null=True, verbose_name='租户id')),
                ('storeId', models.CharField(max_length=32, null=True, verbose_name='门店id')),
                ('storeName', models.CharField(help_text='help_text参数是admin的提示信息', max_length=64, null=True, verbose_name='门店名称')),
                ('deviceSerial', models.CharField(max_length=64, null=True, verbose_name='设备序列号')),
                ('channelNo', models.IntegerField(verbose_name='通道号')),
                ('resourceName', models.CharField(max_length=64, null=True, verbose_name='资源名称')),
                ('userType', models.IntegerField(choices=[(0, '全部'), (1, '会员'), (2, '员工'), (3, '惯偷'), (4, '回头客'), (5, '普通顾客')], verbose_name='用户类型')),
                ('faceToken', models.CharField(max_length=64, null=True, verbose_name='人脸图token')),
                ('faceUrl', models.CharField(max_length=255, null=True, verbose_name='人脸图url')),
                ('standardToken', models.CharField(max_length=64, null=True, verbose_name='标准图token')),
                ('standardUrl', models.CharField(max_length=255, null=True, verbose_name='标准图url')),
                ('bgUrl', models.CharField(max_length=255, null=True, verbose_name='背景图url')),
                ('similarity', models.CharField(max_length=32, null=True, verbose_name='相似度')),
                ('sex', models.IntegerField(choices=[(0, '女'), (1, '男')], verbose_name='性别')),
                ('age', models.IntegerField(verbose_name='年龄')),
                ('glasses', models.IntegerField(choices=[(0, '无眼睛'), (1, '有眼睛')], verbose_name='年龄')),
                ('faceTime', models.CharField(max_length=32, null=True, verbose_name='人脸图时间')),
            ],
            options={
                'verbose_name_plural': '人脸管理',
            },
        ),
    ]
