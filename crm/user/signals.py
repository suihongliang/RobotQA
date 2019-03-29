from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import (
    BaseUser,
    UserInfo,
    BackendUser,
    UserBehavior,
    )
from ..sale.models import (
    CustomerRelation,
    Seller,
    )
from .utils import get_or_create_user


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
def sync_backenduser_info(sender, **kwargs):
    '''
    设置用户名为手机号
    '''
    b_user = kwargs['instance']
    if not b_user.id:
        b_user.username = b_user.mobile
    if b_user.role:
        # 同步销售信息
        if b_user.role.is_seller:
            user = get_or_create_user(b_user.mobile, b_user.company_id)
            if user.userinfo:
                is_seller = b_user.role.is_seller and b_user.is_active
                user.userinfo.is_seller = is_seller
                user.userinfo.save()
            if not hasattr(user, 'seller'):
                Seller.objects.create(user=user)
    else:
        user = get_or_create_user(b_user.mobile, b_user.company_id)
        if user.userinfo:
            user.userinfo.is_seller = False
            user.userinfo.save()


@receiver(pre_save, sender=UserBehavior)
def update_user_access_times(sender, **kwargs):
    '''
    到访更新, 按天计算
    '''
    instance = kwargs['instance']
    if not instance.id:
        if instance.category == 'access':
            if not UserBehavior.objects.filter(
                    category=instance.category,
                    created__date=instance.created.date(),
                    user=instance.user).exists():
                instance.user.userinfo.access_times += 1
                instance.user.userinfo.save()
