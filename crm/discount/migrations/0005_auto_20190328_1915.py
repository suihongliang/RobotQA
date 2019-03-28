# Generated by Django 2.1.1 on 2019-03-28 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0004_coinqrcode_company_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coinrule',
            name='code',
        ),
        migrations.RemoveField(
            model_name='coinrule',
            name='qr_code_url',
        ),
        migrations.AddField(
            model_name='coinrule',
            name='qrcode',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coin_rule', to='discount.CoinQRCode', verbose_name='二维码'),
        ),
    ]
