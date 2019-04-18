# Generated by Django 2.1.1 on 2019-04-18 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discount', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendcoupon',
            name='coupon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discount.Coupon', verbose_name='优惠券'),
        ),
        migrations.AddField(
            model_name='sendcoupon',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserInfo', verbose_name='客户'),
        ),
        migrations.AddField(
            model_name='pointrecord',
            name='rule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='discount.CoinRule', verbose_name='积分规则'),
        ),
        migrations.AddField(
            model_name='pointrecord',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='后台管理'),
        ),
        migrations.AddField(
            model_name='pointrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserInfo', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='coinrule',
            name='qrcode',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coin_rule', to='discount.CoinQRCode', verbose_name='二维码'),
        ),
        migrations.AlterUniqueTogether(
            name='coinrule',
            unique_together={('category', 'company_id')},
        ),
    ]
