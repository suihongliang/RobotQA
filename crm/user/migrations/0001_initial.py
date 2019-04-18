# Generated by Django 2.1.1 on 2019-04-18 11:38

import crm.user.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def init_backend_permission(apps, schema_editor):
    '''
    Init backend permission
    '''
    permissions = (
        ('customer_m', '客户管理',),
        ('product_m', '商品管理',),
        ('coin_m', '积分管理',),
        ('order_m', '订单管理',),
        ('report_m', '报表管理',),
        ('system_m', '系统管理',),
    )
    BackendPermission = apps.get_model('user', 'BackendPermission')
    for code, name in permissions:
        BackendPermission.objects.create(code=code, name=name)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackendUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('mobile', models.CharField(max_length=20, unique=True, verbose_name='手机号')),
                ('username', models.CharField(max_length=30, unique=True, verbose_name='用户名')),
                ('is_active', models.BooleanField(default=True, verbose_name='激活')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Is Staff')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('company_id', models.CharField(max_length=20, verbose_name='公司id')),
                ('name', models.CharField(default='', max_length=25, verbose_name='昵称')),
            ],
            options={
                'verbose_name': '后台用户',
                'swappable': 'AUTH_USER_MODEL',
            },
        ),
        migrations.CreateModel(
            name='BackendGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='备注名称')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='管理员')),
            ],
            options={
                'verbose_name': '用户组',
            },
        ),
        migrations.CreateModel(
            name='BackendPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='权限名称')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('code', models.CharField(max_length=20, verbose_name='编码')),
            ],
            options={
                'verbose_name': '后台权限',
            },
        ),
        migrations.CreateModel(
            name='BackendRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='组名称')),
                ('only_myself', models.BooleanField(default=False, verbose_name='查看自己数据')),
                ('is_seller', models.BooleanField(default=False, verbose_name='是否销售')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('company_id', models.CharField(max_length=20, verbose_name='公司id')),
                ('permissions', models.ManyToManyField(to='user.BackendPermission')),
            ],
            options={
                'verbose_name': '后台群组',
            },
        ),
        migrations.CreateModel(
            name='BaseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(db_index=True, max_length=25, verbose_name='用户手机号')),
                ('company_id', models.CharField(max_length=20, verbose_name='公司id')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活')),
            ],
            options={
                'verbose_name': '用户',
            },
        ),
        migrations.CreateModel(
            name='UserBehavior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('category', models.CharField(max_length=20, verbose_name='类别')),
                ('location', models.CharField(max_length=50, verbose_name='位置')),
            ],
            options={
                'verbose_name': '用户行为',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
        ),
        migrations.CreateModel(
            name='UserOnlineOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('location', models.CharField(max_length=50, verbose_name='点餐位置')),
                ('detail', models.TextField(default='', verbose_name='点餐详情')),
            ],
            options={
                'verbose_name': '用户在线点餐',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.BaseUser', verbose_name='用户')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('name', models.CharField(default='', max_length=25, verbose_name='用户昵称')),
                ('age', models.IntegerField(default=0, verbose_name='年龄')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女'), (0, '未知')], default=0, verbose_name='性别')),
                ('status', models.IntegerField(choices=[(0, '未接触'), (1, '观望中'), (2, '购房成功'), (3, '接触中')], default=0, verbose_name='购房状态')),
                ('note', models.TextField(blank=True, default='', null=True, verbose_name='备注')),
                ('willingness', models.CharField(choices=[('1', '低'), ('2', '中'), ('3', '高'), ('4', '极高')], default='1', max_length=5, verbose_name='客观意愿度')),
                ('self_willingness', models.CharField(choices=[('1', '低'), ('2', '中'), ('3', '高'), ('4', '极高')], default='1', max_length=5, verbose_name='主观意愿度')),
                ('net_worth', models.CharField(default='', max_length=5, verbose_name='净值度')),
                ('is_seller', models.BooleanField(default=False, verbose_name='是否销售')),
                ('last_active_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='活跃时间')),
                ('access_times', models.IntegerField(default=0, verbose_name='到访次数')),
                ('microstore_times', models.IntegerField(default=0, verbose_name='小店次数')),
                ('microstore_seconds', models.IntegerField(default=0, verbose_name='小店总停留秒数')),
                ('sampleroom_times', models.IntegerField(default=0, verbose_name='看样板房次数')),
                ('sampleroom_seconds', models.IntegerField(default=0, verbose_name='看样板房总停留秒数')),
                ('sdver_times', models.IntegerField(default=0, verbose_name='3DVR看房次数')),
                ('coin', models.IntegerField(default=0, verbose_name='积分')),
                ('spend_coin', models.IntegerField(default=0, verbose_name='花费积分')),
                ('extra_data', models.TextField(default='{}', verbose_name='额外参数')),
                ('msg_last_at', models.DateTimeField(default=crm.user.models.before_day, verbose_name='上次读取消息时间')),
                ('industry', models.IntegerField(choices=[(0, '其他'), (1, '政府机关'), (2, '事业单位'), (3, '建筑建材'), (4, '金融投资'), (5, '外贸'), (6, '消费零售'), (7, '制造行业'), (8, '广告传媒'), (9, '医药行业'), (10, '交通运输'), (11, 'IT及互联网'), (12, '教育行业'), (13, '退休'), (14, '商业服务')], default=0, verbose_name='工作行业')),
                ('product_intention', models.CharField(default='', max_length=50, verbose_name='意向产品')),
                ('purchase_purpose', models.CharField(default='', max_length=50, verbose_name='购买用途')),
                ('big_room_seconds', models.IntegerField(default=0, verbose_name='大厅总停留时间')),
            ],
            options={
                'verbose_name': '用户基本信息',
            },
            bases=(models.Model, crm.user.models.UserMobileMixin),
        ),
        migrations.AddField(
            model_name='useronlineorder',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.BaseUser', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='userbehavior',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.BaseUser', verbose_name='用户'),
        ),
        migrations.AlterUniqueTogether(
            name='baseuser',
            unique_together={('mobile', 'company_id')},
        ),
        migrations.AddField(
            model_name='backenduser',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.BackendGroup', verbose_name='用户组'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.BackendRole'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='backendrole',
            unique_together={('name', 'company_id')},
        ),
        # 初始化权限
        migrations.RunPython(init_backend_permission),
    ]
