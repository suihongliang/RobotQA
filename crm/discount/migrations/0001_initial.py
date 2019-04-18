# Generated by Django 2.1.1 on 2019-04-18 11:38

import crm.user.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoinQRCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='qrcode编码')),
                ('qr_code_url', models.URLField(max_length=500, verbose_name='二维码图片链接')),
                ('company_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='公司id')),
            ],
            options={
                'verbose_name': '积分二维码',
                'verbose_name_plural': '积分二维码',
            },
        ),
        migrations.CreateModel(
            name='CoinRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(0, '注册送积分'), (2, '完善个人信息'), (3, '3D看房送积分'), (5, '看样板房送积分'), (8, '活动扫码送积分一'), (9, '活动扫码送积分二'), (10, '活动扫码送积分三')], verbose_name='积分规则')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('coin', models.IntegerField(default=0, verbose_name='赠送积分')),
                ('conditions', models.TextField(default='', verbose_name='Json格式参数')),
                ('company_id', models.CharField(max_length=255, verbose_name='公司编码')),
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
                ('company_id', models.CharField(max_length=255, verbose_name='公司编码')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活')),
            ],
            options={
                'verbose_name': '优惠券',
            },
        ),
        migrations.CreateModel(
            name='PointRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('order', '订单'), ('return_order', '退单'), ('seller_send', '积分赠予'), ('rule_reward', '积分奖励')], default='order', max_length=20, verbose_name='变更类型')),
                ('coin', models.IntegerField(default=0, verbose_name='积分变更值')),
                ('order_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='订单编号')),
                ('return_order_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='退单编号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建于')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新于')),
            ],
            options={
                'verbose_name': '积分变更记录',
                'ordering': ('-created_at',),
                'verbose_name_plural': '积分变更记录',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
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
    ]
