import logging
from rest_framework.decorators import (api_view, permission_classes, authentication_classes, )
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from crm.user.models import BaseUser, UserInfo
from crm.user.utils import ResInfo

logger = logging.getLogger('user_logger')


@api_view(['POST'])
@permission_classes((AllowAny,))
def sync_user(request):
    mobile = request.data.get('mobile')
    store_code = request.data.get('store_code')
    gender = request.data.get('gender')
    nickname = request.data.get('nickname')
    status = request.data.get('status')
    logger.info('sync_user: {}'.format(request.data))
    if not store_code:
        store_code = ''
    if status == 'get':
        user, created = BaseUser.objects.origin_all().get_or_create(mobile=mobile, defaults={'store_code': store_code})
        msg = 'get'
        data = user.id
        logger.info('sync_user: {}'.format((msg, data, created)))
    elif status == 'create':
        user, created = BaseUser.objects.origin_all().get_or_create(mobile=mobile, defaults={'store_code': store_code})
        UserInfo.objects.filter(user__mobile=mobile).update(name=nickname, gender=gender)
        msg = 'create'
        data = user.id
        logger.info('sync_user: {}'.format((msg, data, created)))
    elif status == 'instore':
        user, created = BaseUser.objects.origin_all().update_or_create(
            mobile=mobile, defaults={'store_code': store_code})
        msg = 'instore'
        data = user.id
        logger.info('sync_user: {}'.format((msg, data, created)))
    else:
        data = 0
        msg = 'not found'
    return ResInfo(msg, data)


def external_info(request):
    pass
