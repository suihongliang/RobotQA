# Generated by Django 2.1.1 on 2019-08-08 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gaoyou', '0003_facematch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facematch',
            name='result',
            field=models.IntegerField(blank=True, choices=[(0, '未勾选'), (1, '正确'), (2, '错误')], null=True, verbose_name='复查结果'),
        ),
    ]