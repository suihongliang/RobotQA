from django.db import models


class EveryStatistics(models.Model):
    user_type = (
        (0, "全部"),
        (1, "会员"),
        (2, "员工"),
        (3, "惯偷"),
        (4, "回头客"),
        (5, "普通顾客"),
    )

    UserType = models.IntegerField(choices=user_type, verbose_name='用户类型')
    storeId = models.CharField(max_length=32, null=True, verbose_name='门店id')
    dateTime = models.CharField(max_length=10, null=True, verbose_name='日期')
    male_value = models.IntegerField(verbose_name='男性人数')
    female_value = models.IntegerField(verbose_name='女性人数')
    early_value = models.IntegerField(verbose_name='少年人数')
    young_value = models.IntegerField(verbose_name='青年人数')
    middle_value = models.IntegerField(verbose_name='中年人数')
    old_value = models.IntegerField(verbose_name='老年人数')

    def __str__(self):
        return self.storeId

    class Meta:
        verbose_name_plural = '单日客群属性'


class FaceMatch(models.Model):
    choices = (
        (0, '未勾选'),
        (1, '正确'),
        (2, '错误')
    )
    username = models.CharField(max_length=32, null=True, blank=True, verbose_name='用户名')
    phone = models.CharField(max_length=12, null=True, blank=True, verbose_name='手机号')
    time = models.CharField(max_length=12, null=True, blank=True, verbose_name='匹配时间')
    library_picture = models.CharField(max_length=255, null=True, blank=True, verbose_name='脸库图片')
    grap_picture = models.CharField(max_length=255, null=True, blank=True, verbose_name='抓取图片')
    result = models.IntegerField(choices=choices,null=True, blank=True, verbose_name='复查结果')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '人脸匹配'

