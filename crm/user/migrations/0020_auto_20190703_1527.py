# Generated by Django 2.1.1 on 2019-07-03 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_uservisit_company_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteconfig',
            name='company_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='公司id'),
        ),
        migrations.AlterField(
            model_name='backendgroup',
            name='name',
            field=models.CharField(max_length=20, verbose_name='备注名称'),
        ),
        migrations.AlterField(
            model_name='backendrole',
            name='name',
            field=models.CharField(max_length=20, verbose_name='组名称'),
        ),
        migrations.AlterField(
            model_name='websiteconfig',
            name='http_host',
            field=models.CharField(max_length=100, unique=True, verbose_name='域名'),
        ),
        migrations.AlterUniqueTogether(
            name='backendgroup',
            unique_together={('name', 'manager')},
        ),
    ]
