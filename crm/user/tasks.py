from celery.task import Task
from django.conf import settings
from crm.user.models import UserBehavior, UserInfo
from django.utils import timezone
from crm.user.utils import generate_sign
import datetime
import requests
import logging

logger = logging.getLogger('user_logger')


class SendSMS(Task):
    def run(self, user_id):
        user = UserInfo.objects.select_related('customerrelation', 'user').filter(user_id=user_id).first()
        print('----------start:{}----------'.format(user_id))
        if user.is_seller:
            return
        seller = user.customerrelation.seller
        if not seller:
            return
        today_behavior = UserBehavior.objects.filter(
            user_id=user_id, category='access', created__date=timezone.now().date()).order_by('-created')
        if today_behavior.exists():
            now = timezone.now()
            berfore_time = now - datetime.timedelta(hours=4)
            behavior = UserBehavior.objects.filter(
                user_id=user_id, category='access', created__range=[berfore_time, now])
            if behavior.exists():
                return
        seller_mobile = seller.user.mobile
        customer_mobile = user.mobile
        mark_name = user.customerrelation.mark_name
        name = mark_name if mark_name else user.name if user.name else customer_mobile
        params = dict(seller_mobile=seller_mobile, name=name)
        sign = generate_sign(params)
        params['sign'] = sign
        print('-------------send-------------')
        res = requests.get(settings.ERP_JIAN24_URL + '/crm/send-msg/', params=params)
        if res.ok:
            data = res.json()
            logger.info('{}.{}: {}'.format(__name__, 'SendSMS', user_id, data))
        print('-------------error------------')
