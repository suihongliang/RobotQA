from django.db import models
from django.utils import timezone


class BaseUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def origin_all(self):
        return super().get_queryset()


class UserMobileMixin():

    @property
    def mobile(self):
        return self.user.mobile


class BaseUser(models.Model):

    mobile = models.CharField(
        max_length=25, db_index=True, verbose_name='用户手机号')
    store_code = models.CharField(
        verbose_name='门店编码', max_length=255)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    is_active = models.BooleanField(
        verbose_name="是否激活", default=True)

    objects = BaseUserManager()

    def __str__(self):
        return self.mobile

    class Meta:
        verbose_name = '用户'
        unique_together = (("mobile", "store_code"),)


class UserInfo(models.Model, UserMobileMixin):
    '''
    用户基本信息
    '''

    user = models.OneToOneField(
        BaseUser, on_delete=models.CASCADE, primary_key=True,
        verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    name = models.CharField(
        max_length=25, verbose_name='用户昵称', default='')
    age = models.IntegerField(
        verbose_name='年龄', default=-1)
    gender = models.IntegerField(
        choices=[
            (0, '男'),
            (1, '女'),
        ], default=0, verbose_name='性别')
    status = models.IntegerField(
        choices=[
            (0, '接触中'),
            (1, '观望中'),
            (2, '购房成功'),
        ], default=0, verbose_name='购房状态')
    note = models.TextField(
        verbose_name='备注', default='')
    willingness = models.CharField(
        max_length=5, verbose_name='意愿度', default='')
    net_worth = models.CharField(
        max_length=5, verbose_name='净值度', default='')
    is_seller = models.BooleanField(
        verbose_name='是否销售', default=False)

    def __str__(self):
        return str(self.user)

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
        verbose_name='创建时间', default=timezone.now)
    category = models.IntegerField(
        choices=[
            (0, '男'),
        ], default=0, verbose_name='类别')
    location = models.CharField(
        max_length=50, verbose_name='位置')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户行为'
