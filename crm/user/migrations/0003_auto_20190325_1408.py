# Generated by Django 2.1.1 on 2019-03-25 06:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190325_1151'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='backendrole',
            unique_together={('name', 'store_code')},
        ),
    ]
