# Generated by Django 2.1.1 on 2019-07-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0003_auto_20190715_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='name',
            field=models.CharField(default='', max_length=25, verbose_name='姓名'),
        ),
    ]
