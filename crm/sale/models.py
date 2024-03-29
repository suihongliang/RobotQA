from django.db import models
from django.utils import timezone
from ..user.models import (
    UserMobileMixin,
    BaseUser,
    UserInfo,
    )


class QRCode(models.Model):

    code = models.CharField(
        verbose_name="qrcode编码", max_length=50)
    qr_code_url = models.URLField(
        verbose_name="二维码图片链接", max_length=500)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id", null=True, blank=True)

    def __str__(self):
        return "{}:{}".format(self.company_id, self.code)

    class Meta:
        verbose_name = verbose_name_plural = "销售二维码"
        unique_together = (("code", "company_id"),)


class Seller(models.Model, UserMobileMixin):

    user = models.OneToOneField(
        BaseUser, on_delete=models.CASCADE, primary_key=True,
        verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    qrcode = models.OneToOneField(QRCode,
                                  verbose_name="二维码",
                                  on_delete=models.SET_NULL,
                                  related_name="seller",
                                  blank=True, null=True)
    # profession = models.CharField(verbose_name="职业", max_length=100, blank=True, null=True)
    # avatar = models.URLField(verbose_name="头像链接", max_length=500, blank=True, null=True)
    # name = models.CharField(max_length=25, verbose_name='姓名', default='')

    @property
    def is_active(self):
        return self.user.userinfo.is_seller

    @property
    def mobile(self):
        return self.user.mobile

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '销售人员'


class CustomerRelation(models.Model):

    seller = models.ForeignKey(
        Seller, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="销售")
    user = models.OneToOneField(
        UserInfo, on_delete=models.CASCADE, primary_key=True,
        verbose_name="客户")
    mark_name = models.CharField(
        max_length=25, verbose_name='备注昵称', default='')
    created = models.DateTimeField(
        verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return str(self.seller)

    class Meta:
        verbose_name = '客户关系'
