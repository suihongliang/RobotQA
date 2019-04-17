from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import json

#
# class Store(models.Model):
#
#     store_code = models.CharField(
#         verbose_name='门店编码', max_length=255, unique=True)
#     company_id = models.CharField(
#         max_length=20, verbose_name="公司id")
#
#     def __str__(self):
#         return '.'.join([self.company_id, self.store_code])
#
#     class Meta:
#         verbose_name = '门店关系'


class BackendUserManager(BaseUserManager):

    def _create_user(self, username, mobile, password,
                     is_staff, is_superuser, **extra_fields):
        """
        根据用户名和密码创建一个用户
        """
        if not mobile:
            raise ValueError('mobile必须填写')
        user = self.model(mobile=mobile,
                          username=username,
                          is_active=True,
                          is_staff=is_staff,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, mobile, password=None, **extra_fields):
        return self._create_user(mobile, mobile, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, mobile, password, **extra_fields):
        return self._create_user(username, mobile, password, True, True,
                                 **extra_fields)


class BaseUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def origin_all(self):
        return super().get_queryset()


class UserMobileMixin():

    @property
    def mobile(self):
        return self.user.mobile


class BackendPermission(models.Model):

    name = models.CharField(
        max_length=20, unique=True,
        verbose_name="权限名称")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    code = models.CharField(
        max_length=20, verbose_name='编码')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '后台权限'


class BackendRole(models.Model):

    name = models.CharField(
        max_length=20, unique=True, verbose_name="组名称")
    permissions = models.ManyToManyField(
        BackendPermission)
    only_myself = models.BooleanField(
        verbose_name='查看自己数据', default=False)
    is_seller = models.BooleanField(
        verbose_name='是否销售', default=False)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '后台群组'
        unique_together = (("name", "company_id"),)


class BackendGroup(models.Model):

    name = models.CharField(
        max_length=20, unique=True,
        verbose_name="备注名称")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    manager = models.ForeignKey(
        "user.BackendUser", null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="管理员")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户组'


class BackendUser(AbstractBaseUser, PermissionsMixin):

    mobile = models.CharField(
        max_length=20, unique=True,
        verbose_name="手机号")
    username = models.CharField(
        verbose_name="用户名", max_length=30, unique=True)
    is_active = models.BooleanField(
        verbose_name="激活", default=True)
    is_staff = models.BooleanField(
        verbose_name="Is Staff", default=False)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    role = models.ForeignKey(
        BackendRole, null=True, blank=True, on_delete=models.SET_NULL)
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")
    name = models.CharField(
        max_length=25, verbose_name='昵称', default='')
    group = models.ForeignKey(
        BackendGroup, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="用户组")

    objects = BackendUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', ]

    def has_backend_perms(self):
        pass

    def __str__(self):
        return self.mobile

    class Meta:
        verbose_name = '后台用户'
        swappable = 'AUTH_USER_MODEL'


class BaseUser(models.Model):

    mobile = models.CharField(
        max_length=25, db_index=True, verbose_name='用户手机号')
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    is_active = models.BooleanField(
        verbose_name="是否激活", default=True)

    objects = BaseUserManager()

    def __str__(self):
        return self.mobile

    class Meta:
        verbose_name = '用户'
        unique_together = (("mobile", "company_id"),)


def before_day():
    return timezone.now() - timedelta(days=1)


class UserInfo(models.Model, UserMobileMixin):
    '''
    用户基本信息
    '''
    INDUSTRY = [
        (0, '其他'),
        (1, '政府机关'),
        (2, '事业单位'),
        (3, '建筑建材'),
        (4, '金融投资'),
        (5, '外贸'),
        (6, '消费零售'),
        (7, '制造行业'),
        (8, '广告传媒'),
        (9, '医药行业'),
        (10, '交通运输'),
        (11, 'IT及互联网'),
        (12, '教育行业'),
        (13, '退休'),
        (14, '商业服务'),
    ]

    user = models.OneToOneField(
        BaseUser, on_delete=models.CASCADE, primary_key=True,
        verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    name = models.CharField(
        max_length=25, verbose_name='用户昵称', default='')
    age = models.IntegerField(
        verbose_name='年龄', default=0)
    gender = models.IntegerField(
        choices=[
            (1, '男'),
            (2, '女'),
            (0, '未知'),
        ], default=0, verbose_name='性别')
    status = models.IntegerField(
        choices=[
            (0, '未接触'),
            (1, '观望中'),
            (2, '购房成功'),
            (3, '接触中'),
        ], default=0, verbose_name='购房状态')
    note = models.TextField(
        verbose_name='备注', default='')
    willingness = models.CharField(
        choices=[
            ('1', '低'),
            ('2', '中'),
            ('3', '高'),
            ('4', '极高'),
        ], max_length=5, verbose_name='意愿度', default='1')
    net_worth = models.CharField(
        max_length=5, verbose_name='净值度', default='')
    is_seller = models.BooleanField(
        verbose_name='是否销售', default=False)
    last_active_time = models.DateTimeField(
        verbose_name='活跃时间', default=timezone.now)
    access_times = models.IntegerField(
        verbose_name='到访次数', default=0)
    sampleroom_times = models.IntegerField(
        verbose_name='看样板房次数', default=0)
    sampleroom_seconds = models.IntegerField(
        verbose_name="看样板房总停留秒数", default=0)
    sdver_times = models.IntegerField(
        verbose_name='3DVR看房次数', default=0)
    coin = models.IntegerField(
        verbose_name='积分', default=0)
    spend_coin = models.IntegerField(
        verbose_name='花费积分', default=0)
    extra_data = models.TextField(
        verbose_name='额外参数', default=json.dumps({}))
    msg_last_at = models.DateTimeField(
        verbose_name="上次读取消息时间",
        default=before_day)
    industry = models.IntegerField(
        verbose_name='工作行业', choices=INDUSTRY, default=0)
    product_intention = models.CharField(
        max_length=50, verbose_name='意向产品', default='')
    purchase_purpose = models.CharField(
        max_length=50, verbose_name='购买用途', default='')

    def get_extra_data_json(self):
        try:
            return json.loads(self.extra_data)
        except json.JSONDecodeError:
            return {}

    def __str__(self):
        return str(self.user.mobile)

    class Meta:
        verbose_name = '用户基本信息'


class UserOnlineOrder(models.Model, UserMobileMixin):
    '''
    用户在线点餐记录
    '''

    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    location = models.CharField(
        max_length=50, verbose_name='点餐位置')
    detail = models.TextField(
        verbose_name='点餐详情', default='')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户在线点餐'


class UserBehavior(models.Model, UserMobileMixin):

    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', auto_now_add=True)
    """
    access: 到访(摄像头)
    signup: 注册
    sampleroom: 样板房
    sellerbind: 绑定销售
    3dvr: 3d看房
    microstore: 门店到访
    """
    category = models.CharField(
        verbose_name='类别', max_length=20)
    location = models.CharField(
        max_length=50, verbose_name='位置')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户行为'
