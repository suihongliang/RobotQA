# Generated by Django 2.1.1 on 2019-06-21 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_websiteconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='websiteconfig',
            name='http_host',
            field=models.CharField(max_length=20, unique=True, verbose_name='域名'),
        ),
    ]
