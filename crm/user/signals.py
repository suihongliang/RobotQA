from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    BaseUser,
    UserInfo,
    )


@receiver(post_save, sender=BaseUser)
def sync_create_userinfo(sender, **kwargs):
    '''
    同步创建用户信息
    '''
    user = kwargs['instance']
    if kwargs['created']:
        UserInfo.objects.create(user=user)
