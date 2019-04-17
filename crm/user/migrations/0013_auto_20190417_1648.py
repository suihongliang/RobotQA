# Generated by Django 2.1.1 on 2019-04-17 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20190415_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='willingness',
            field=models.CharField(choices=[('1', '低'), ('2', '中'), ('3', '高'), ('4', '极高')], default='1', max_length=5, verbose_name='意愿度'),
        ),
    ]
