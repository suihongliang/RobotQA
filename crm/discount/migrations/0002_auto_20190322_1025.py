# Generated by Django 2.1.1 on 2019-03-22 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coinrule',
            name='store_code',
            field=models.CharField(default='', max_length=255, verbose_name='门店编码'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coinrule',
            name='category',
            field=models.IntegerField(choices=[(0, '注册送积分'), (1, '到访送积分'), (2, '问卷积分'), (3, '3D看房送积分'), (4, '签到送积分'), (5, '看样板房送积分'), (6, '活动扫码送积分1'), (7, '活动扫码送积分2'), (8, '活动扫码送积分3'), (9, '活动扫码送积分4'), (10, '活动扫码送积分5')], verbose_name='购房状态'),
        ),
        migrations.AlterUniqueTogether(
            name='coinrule',
            unique_together={('category', 'store_code')},
        ),
    ]
