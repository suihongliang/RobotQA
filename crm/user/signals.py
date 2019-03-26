from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import (
    BaseUser,
    UserInfo,
    BackendUser,
    )
from ..sale.models import (
    CustomerRelation,
    )


@receiver(post_save, sender=BaseUser)
def sync_create_userinfo(sender, **kwargs):
    '''
    同步创建用户信息
    '''
    user = kwargs['instance']
    if kwargs['created']:
        userinfo = UserInfo.objects.create(user=user)
        CustomerRelation.objects.create(user=userinfo)


@receiver(pre_save, sender=BackendUser)
def create_backenduser(sender, **kwargs):
    '''
    设置用户名为手机号
    '''
    user = kwargs['instance']
    if not user.id:
        user.username = user.mobile
