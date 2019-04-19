from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    PointRecord,
    )


@receiver(post_save, sender=PointRecord)
def sync_coin_userinfo(sender, **kwargs):
    '''
    同步创建用户信息
    '''

    instance = kwargs['instance']
    instance.user.coin += instance.coin

    if instance.coin < 0:
        instance.user.spend_coin += abs(instance.coin)
    instance.user.save()
