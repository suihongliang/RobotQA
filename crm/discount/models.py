from django.db import models
from django.utils import timezone
from ..user.models import (
    UserInfo,
    )
from ..sale.models import (
    Seller,
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
        ], verbose_name='购房状态')
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
        return self.name

    class Meta:
        verbose_name = '积分规则'
        unique_together = (('category', 'store_code'),)


class Coupon(models.Model):

    description = models.CharField(
        verbose_name="描述", max_length=500, default='')
    discount = models.CharField(
        verbose_name="折扣率", max_length=10)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    store_code = models.CharField(
        verbose_name='门店编码', max_length=255)

    def __str__(self):
        return str(self.discunt)

    class Meta:
        verbose_name = '优惠券'


class SendCoupon(models.Model):

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, verbose_name="销售")
    user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, verbose_name="客户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, verbose_name="优惠券")

    def __str__(self):
        return str(self.seller)

    class Meta:
        verbose_name = '用户优惠券'
