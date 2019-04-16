# Generated by Django 2.1.1 on 2019-04-16 11:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0016_auto_20190416_1115'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pointrecord',
            options={'ordering': ('-created_at',), 'verbose_name': '积分变更记录', 'verbose_name_plural': '积分变更记录'},
        ),
        migrations.AddField(
            model_name='pointrecord',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='创建于'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pointrecord',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新于'),
        ),
    ]
