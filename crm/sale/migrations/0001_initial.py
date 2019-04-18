# Generated by Django 2.1.1 on 2019-04-18 11:38

import crm.user.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerRelation',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.UserInfo', verbose_name='客户')),
                ('mark_name', models.CharField(default='', max_length=25, verbose_name='备注昵称')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '客户关系',
            },
        ),
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='qrcode编码')),
                ('qr_code_url', models.URLField(max_length=500, verbose_name='二维码图片链接')),
                ('company_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='公司id')),
            ],
            options={
                'verbose_name': '销售二维码',
                'verbose_name_plural': '销售二维码',
            },
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.BaseUser', verbose_name='用户')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('qrcode', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seller', to='sale.QRCode', verbose_name='二维码')),
            ],
            options={
                'verbose_name': '销售人员',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
        ),
        migrations.AddField(
            model_name='customerrelation',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale.Seller', verbose_name='销售'),
        ),
    ]
