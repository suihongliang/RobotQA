# Generated by Django 2.1.1 on 2019-05-07 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0004_auto_20190424_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coinrule',
            name='category',
            field=models.IntegerField(choices=[(0, '注册送积分'), (2, '完善个人信息'), (3, '3D看房送积分'), (5, '看样板房送积分'), (6, '绑定销售'), (8, '活动扫码一'), (9, '活动扫码二'), (10, '活动扫码三'), (11, '活动扫码四'), (12, '活动扫码五'), (13, '活动扫码六'), (14, '活动扫码七'), (15, '活动扫码八'), (16, '活动扫码九'), (17, '活动扫码十'), (18, '活动扫码十一'), (19, '活动扫码十二'), (20, '活动扫码十三'), (21, '活动扫码十四'), (22, '活动扫码十五'), (23, '活动扫码十六'), (24, '活动扫码十七'), (25, '活动扫码十八'), (26, '活动扫码十九'), (27, '活动扫码二十'), (28, '活动扫码二一'), (29, '活动扫码二二'), (30, '活动扫码二三'), (31, '活动扫码二四'), (32, '活动扫码二五'), (33, '活动扫码二六'), (34, '活动扫码二七'), (35, '活动扫码二八')], verbose_name='积分规则'),
        ),
    ]
