from django.db import models
from django.utils import timezone
from ..user.models import (
    UserInfo,
    UserMobileMixin,
    )
# from ..sale.models import (
#     Seller,
#     )
from ..user.models import (
    BackendUser,
    )


class CoinRule(models.Model):

    category = models.IntegerField(
        choices=[
            (0, '注册送积分'),
            (1, '到访送积分'),
            (2, '问卷积分'),
            (3, '3D看房送积分'),
            (4, '签到送积分'),
            (5, '看样板房送积分'),
            (6, '活动扫码送积分1'),
            (7, '活动扫码送积分2'),
            (8, '活动扫码送积分3'),
            (9, '活动扫码送积分4'),
            (10, '活动扫码送积分5'),
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
    code = models.CharField(
        verbose_name="qrcode编码(非必填)", max_length=50, default='')
    qr_code_url = models.CharField(
        verbose_name="二维码图片链接(非必填)", max_length=500, default='')
    store_code = models.CharField(
        verbose_name='门店编码', max_length=255)

    def __str__(self):
        return self.get_category_display()

    class Meta:
        verbose_name = '积分规则'
        unique_together = (('category', 'store_code'),)


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
    store_code = models.CharField(
        verbose_name='门店编码', max_length=255)
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
