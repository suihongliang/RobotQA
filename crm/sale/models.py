from django.db import models
from django.utils import timezone
from ..user.models import (
    BaseUser,
    UserInfo,
    )


class Seller(models.Model):

    user = models.OneToOneField(
        BaseUser, on_delete=models.CASCADE, primary_key=True,
        verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    code = models.CharField(
        verbose_name="qrcode编码", max_length=50)
    qr_code_url = models.CharField(
        verbose_name="二维码图片链接", max_length=500)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '销售人员'


class CustomerRelation(models.Model):

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, verbose_name="销售")
    user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, verbose_name="客户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)

    def __str__(self):
        return str(self.seller)

    class Meta:
        verbose_name = '客户关系'
