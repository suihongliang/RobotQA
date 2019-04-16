import json

from django.db import models
from django.utils import timezone

from crm.sale.models import Seller
from ..user.models import (
    UserInfo,
    UserMobileMixin,
    BackendUser,
    BaseUser)
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


class PointRecord(models.Model, UserMobileMixin):
    CHANGE_TYPE = (
        ('order', '订单'),
        ('return_order', '退单'),
        ('seller_send', '积分赠予'),
        ('rule_reward', '积分奖励')
    )

    change_type = models.CharField(
        verbose_name="变更类型", choices=CHANGE_TYPE, max_length=20, default='order')
    user = models.ForeignKey(
        UserInfo, verbose_name="用户", on_delete=models.CASCADE)
    coin = models.IntegerField(verbose_name="积分变更值", default=0)
    order_no = models.CharField(
        verbose_name="订单编号", max_length=100, blank=True, null=True)
    return_order_no = models.CharField(
        verbose_name="退单编号", max_length=100, blank=True, null=True)
    seller = models.ForeignKey(
        BackendUser, verbose_name="后台管理", on_delete=models.SET_NULL, null=True, blank=True)
    rule = models.ForeignKey(
        CoinRule, verbose_name="积分规则", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="创建于", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新于", auto_now=True)

    def __str__(self):
        return self.get_change_type_display()

    class Meta:
        verbose_name = verbose_name_plural = "积分变更记录"
        ordering = ('-created_at',)

    @property
    def change_by(self):
        if self.change_type == 'order':
            return self.order_no
        elif self.change_type == 'return_order':
            return self.return_order_no
        elif self.change_type == 'seller_send':
            return self.seller.mobile
        else:
            return self.rule.get_category_display()
