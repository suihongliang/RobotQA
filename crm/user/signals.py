from django.db.models import F
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone


from crm.discount.models import CoinRule, PointRecord
from .models import (
    BaseUser,
    UserInfo,
    BackendUser,
    UserBehavior,
    BackendRole,
    StayTime)
from ..sale.models import (
    CustomerRelation,
    Seller,
    )
from .utils import get_or_create_user
from crm.user.tasks import SendSMS
import datetime
from rest_framework.serializers import ValidationError


def update_seller_info(b_user):
    if b_user.role:
        user = get_or_create_user(b_user.mobile, b_user.company_id)
        if user.userinfo:
            # is_seller = b_user.role.is_seller and b_user.is_active
            is_seller = b_user.is_active
            user.userinfo.is_seller = is_seller
            user.userinfo.save()
        if not hasattr(user, 'seller') and b_user.role.is_seller:
            Seller.objects.create(user=user)
    else:
        user = get_or_create_user(b_user.mobile, b_user.company_id)
        if user.userinfo:
            user.userinfo.is_seller = False
            user.userinfo.save()


def send_msg(instance, user_behavior_record):
    user_id = instance.user_id
    user = UserInfo.objects.select_related('customerrelation', 'user').filter(user_id=user_id).first()
    seller_obj = user.customerrelation.seller
    if not user.is_seller and seller_obj:
        if user_behavior_record:
            now = timezone.now()
            berfore_time = now - datetime.timedelta(hours=4)
            behavior = UserBehavior.objects.filter(
                user_id=user_id, category='access', created__range=[berfore_time, now])
            if not behavior.exists():
                SendSMS.apply_async(args=[user_id])
        else:
            SendSMS.apply_async(args=[user_id])


def negative_activity(instance, rule):
    coin = rule.coin
    user_coin = instance.user.userinfo.coin
    if user_coin + coin < 0:
        raise ValidationError(dict(msg='积分不足'))
    else:
        PointRecord.objects.create(
            user_id=instance.user_id,
            rule=rule,
            coin=rule.coin,
            change_type='rule_reward')


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
        rule = CoinRule.objects.get(category=0)
        userinfo = UserInfo.objects.create(user=user)
        CustomerRelation.objects.create(user=userinfo)
        UserBehavior.objects.create(user=user, category='signup', location='')
        PointRecord.objects.create(user_id=user.id,
                                   rule=rule,
                                   coin=rule.coin,
                                   change_type='rule_reward')


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
        filter_query.update({'created__date': timezone.now().date()})
    user_behavior_record = UserBehavior.objects.filter(**filter_query).exists()

    category_flag = None
    if category == 'access':
        # 某天第一次到访
        category_flag = 1
        if not user_behavior_record:  # 每天一次
            instance.user.userinfo.access_times += 1
            instance.user.userinfo.last_active_time = timezone.now()
            instance.user.userinfo.save()
        send_msg(instance, user_behavior_record)

    elif category == 'sampleroom':
        # 看样板房
        if instance.location == 'out':
            ub = UserBehavior.objects.filter(
                user_id=instance.user_id,
                category=category,
                created__date=timezone.now().date()).order_by('-created').first()
            if ub and ub.location == 'in':
                stay_seconds = (timezone.now() - ub.created).seconds
                instance.user.userinfo.sampleroom_seconds += stay_seconds
                obj, created = StayTime.objects.get_or_create(user_id=instance.user_id, created_at=timezone.now().date())
                obj.sample_seconds = F('sample_seconds') + stay_seconds
                obj.save()
        else:
            instance.user.userinfo.sampleroom_times += 1
        instance.user.userinfo.save()
        category_flag = 5
    elif category == 'microstore':
        # 门店到访
        if instance.location == 'out':
            ub = UserBehavior.objects.filter(
                user_id=instance.user_id,
                category=category,
                created__date=timezone.now().date()).order_by('-created').first()
            if ub and ub.location == 'in':
                stay_seconds = (timezone.now() - ub.created).seconds
                instance.user.userinfo.microstore_seconds += stay_seconds
                obj, created = StayTime.objects.get_or_create(user_id=instance.user_id, created_at=timezone.now().date())
                obj.micro_seconds = F('micro_seconds') + stay_seconds
                obj.save()
        else:
            if not user_behavior_record:  # 每天一次
                instance.user.userinfo.microstore_times += 1
        instance.user.userinfo.save()
        category_flag = 7
    # elif category == 'activity1':
    #     # 活动扫码送积分3
    #     category_flag = 8
    # elif category == 'activity2':
    #     # 活动扫码送积分4
    #     category_flag = 9
    # elif category == 'activity3':
    #     # 活动扫码送积分5
    #     category_flag = 10

    elif category.startswith('activity'):
        # 活动扫码送积分
        category_dict = {'activity'+str(i-7): i for i in range(8, CoinRule.ACTIVITY[-1][0]+1)}
        category_flag = category_dict.get(category)

    rule = CoinRule.objects.filter(category=category_flag).first()
    if not rule:
        return

    # 负积分活动
    if rule.coin < 0:
        negative_activity(instance, rule)
        return

    if user_behavior_record:  # 记录存在则不加积分
        return

    # rule = CoinRule.objects.filter(category=category_flag).first()
    # if not rule:
    #     return
    PointRecord.objects.create(
        user_id=instance.user_id,
        rule=rule,
        coin=rule.coin,
        change_type='rule_reward')
