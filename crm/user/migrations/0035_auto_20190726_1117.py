# Generated by Django 2.1.1 on 2019-07-26 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0034_auto_20190726_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='target_of_buy_house',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='购房目的'),
        ),
    ]