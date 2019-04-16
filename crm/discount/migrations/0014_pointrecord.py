# Generated by Django 2.1.1 on 2019-04-16 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0007_auto_20190411_2014'),
        ('user', '0012_auto_20190415_1453'),
        ('discount', '0013_auto_20190415_1738'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('order', '订单'), ('return_order', '退单'), ('seller_send', '销售赠予'), ('rule_reward', '积分奖励')], default='order', max_length=20, verbose_name='变更类型')),
                ('coin', models.IntegerField(default=0, verbose_name='积分变更值')),
                ('order_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='订单编号')),
                ('return_order_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='退单编号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建于')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新于')),
                ('rule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='discount.CoinRule', verbose_name='积分规则')),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale.Seller', verbose_name='销售')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserInfo', verbose_name='用户')),
            ],
            options={
                'verbose_name': '积分变更记录',
                'verbose_name_plural': '积分变更记录',
                'ordering': ('-created_at',),
            },
        ),
    ]
