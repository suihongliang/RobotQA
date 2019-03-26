# Generated by Django 2.1.1 on 2019-03-26 05:53

import crm.user.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoinRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(0, '注册送积分'), (1, '到访送积分'), (2, '问卷积分'), (3, '3D看房送积分'), (4, '签到送积分'), (5, '看样板房送积分'), (6, '活动扫码送积分1'), (7, '活动扫码送积分2'), (8, '活动扫码送积分3'), (9, '活动扫码送积分4'), (10, '活动扫码送积分5')], verbose_name='购房状态')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('coin', models.IntegerField(default=0, verbose_name='赠送积分')),
                ('conditions', models.TextField(default='', verbose_name='Json格式参数')),
                ('code', models.CharField(default='', max_length=50, verbose_name='qrcode编码(非必填)')),
                ('qr_code_url', models.CharField(default='', max_length=500, verbose_name='二维码图片链接(非必填)')),
                ('store_code', models.CharField(max_length=255, verbose_name='门店编码')),
            ],
            options={
                'verbose_name': '积分规则',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default='', max_length=500, verbose_name='描述')),
                ('discount', models.CharField(max_length=10, verbose_name='折扣率')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('store_code', models.CharField(max_length=255, verbose_name='门店编码')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活')),
            ],
            options={
                'verbose_name': '优惠券',
            },
        ),
        migrations.CreateModel(
            name='SendCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '用户优惠券',
            },
        ),
        migrations.CreateModel(
            name='UserCoinRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('coin', models.IntegerField(default=0, verbose_name='赠送积分')),
                ('update_status', models.BooleanField(default=False, verbose_name='更新状态')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discount.CoinRule', verbose_name='类型')),
            ],
            options={
                'verbose_name': '用户积分记录',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
        ),
    ]
