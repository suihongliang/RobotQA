# Generated by Django 2.1.1 on 2019-03-20 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='is_seller',
            field=models.BooleanField(default=False, verbose_name='是否销售'),
        ),
    ]
