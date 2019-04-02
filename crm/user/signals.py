import json

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from crm.discount.models import UserCoinRecord, CoinRule
from .models import (
    BaseUser,
    UserInfo,
    BackendUser,
    UserBehavior,
    BackendRole,
    )
from ..sale.models import (
    CustomerRelation,
    Seller,
    )
from .utils import get_or_create_user


def update_seller_info(b_user):
    if b_user.role:
        user = get_or_create_user(b_user.mobile, b_user.company_id)
        if user.userinfo:
            is_seller = b_user.role.is_seller and b_user.is_active
            user.userinfo.is_seller = is_seller
            user.userinfo.save()
        if not hasattr(user, 'seller') and b_user.role.is_seller:
            Seller.objects.create(user=user)
    else:
        user = get_or_create_user(b_user.mobile, b_user.company_id)
        if user.userinfo:
            user.userinfo.is_seller = False
            user.userinfo.save()


@receiver(post_save, sender=BackendRole)
def sync_backendrole_info(sender, **kwargs):
    instance = kwargs['instance']
    for b_user in instance.backenduser_set.all():
        update_seller_info(b_user)


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
    update_seller_info(b_user)


@receiver(pre_save, sender=UserBehavior)
def user_behavior_event(sender, **kwargs):
    '''
    到访更新, 按天计算
    '''
    instance = kwargs['instance']
    category = instance.category
    filter_query = {'category': category, 'user': instance.user}
    if category not in ('signup', 'sellerbind'):  # 注册 绑定销售
        filter_query.update({'created__date': instance.created.date()})
    user_behavior_record = UserBehavior.objects.filter(**filter_query).exists()

    if user_behavior_record:
        return
    category_flag = None
    if category == 'access':
        # 某天第一次到访
        category_flag = 1
        instance.user.userinfo.access_times += 1
        instance.user.userinfo.save()
    elif category == '3dvr':
        # 3D看房
        category_flag = 3
    elif category == 'sampleroom':
        # 看样板房
        category_flag = 5
    elif category == 'signup':
        # 注册
        category_flag = 0
    elif category == 'sellerbind':
        # 绑定销售
        category_flag = 6
    elif category == 'microstore':
        # 门店到访
        category_flag = 7

    rule = CoinRule.objects.filter(category=category_flag).first()
    if not rule:
        return
    UserCoinRecord.objects.create(
        user_id=instance.user_id,
        rule=rule,
        coin=rule.coin,
        update_status=True,
        extra_data=json.dumps({'mobile': instance.user.mobile}))
