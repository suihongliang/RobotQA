from django.db import models
from django.utils import timezone
from ..user.models import (
    UserInfo,
    UserMobileMixin,
    BackendUser,
    )
# from ..sale.models import (
#     Seller,
#     )


class CoinQRCode(models.Model):

    code = models.CharField(
        verbose_name="qrcode编码", max_length=50, unique=True)
    qr_code_url = models.URLField(
        verbose_name="二维码图片链接", max_length=500)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id", null=True, blank=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = verbose_name_plural = "积分二维码"


class CoinRule(models.Model):

    category = models.IntegerField(
        choices=[
            (0, '注册送积分'),
            # (1, '到访送积分'),
            (2, '完善个人信息'),
            (3, '3D看房送积分'),
            # (4, '签到送积分'),
            (5, '看样板房送积分'),
            # (6, '绑定销售'),
            # (7, '完善个人信息'),
            (8, '活动扫码送积分一'),
            (9, '活动扫码送积分二'),
            (10, '活动扫码送积分三'),
        ], verbose_name='积分规则')
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    coin = models.IntegerField(
        verbose_name='赠送积分', default=0)
    '''
    扫码送积分: {'code': '1234', 'qr_code_url': 'http://123'}
    '''
    conditions = models.TextField(
        verbose_name="Json格式参数", default='')
    qrcode = models.OneToOneField(CoinQRCode,
                                  verbose_name="二维码",
                                  on_delete=models.SET_NULL,
                                  related_name="coin_rule",
                                  blank=True, null=True)
    company_id = models.CharField(
        verbose_name='公司编码', max_length=255)

    def __str__(self):
        return self.get_category_display()

    class Meta:
        verbose_name = '积分规则'
        unique_together = (('category', 'company_id'),)


class UserCoinRecord(models.Model, UserMobileMixin):

    user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, verbose_name="用户")
    rule = models.ForeignKey(
        CoinRule, on_delete=models.CASCADE, verbose_name="类型",
        null=True, blank=True)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    coin = models.IntegerField(
        verbose_name='赠送积分', default=0)
    update_status = models.BooleanField(
        default=False, verbose_name='更新状态')
    extra_data = models.TextField(
        verbose_name='额外参数', default='')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户积分记录'


class Coupon(models.Model):

    description = models.CharField(
        verbose_name="描述", max_length=500, default='')
    discount = models.CharField(
        verbose_name="折扣率", max_length=10)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    company_id = models.CharField(
        verbose_name='公司编码', max_length=255)
    is_active = models.BooleanField(
        verbose_name='是否激活', default=True)

    def __str__(self):
        return str(self.discount)

    class Meta:
        verbose_name = '优惠券'


class SendCoupon(models.Model):

    backenduser = models.ForeignKey(
        BackendUser, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="后台用户")
    user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, verbose_name="客户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, verbose_name="优惠券")

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户优惠券'
