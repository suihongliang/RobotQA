import logging
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from crm.sale.models import Seller, CustomerRelation
from crm.user.models import UserInfo, BaseUser
from crm.user.utils import ResInfo

logger = logging.getLogger('sale_logger')


def bind_relation(user_mobile, seller_mobile, user_name, store_code):
    try:
        user = UserInfo.objects.get(user__mobile=user_mobile)
        seller = Seller.objects.get(user__mobile=seller_mobile)
        relation, created = CustomerRelation.objects.get_or_create(seller=seller, user=user)

        if created:
            if user_name:
                user.name = user_name
                user.save(update_fields=['name'])
            if store_code:
                BaseUser.objects.filter(mobile=user_mobile).update(store_code=store_code)
            result = '{}: add customer: {} success'.format(seller_mobile, user_mobile)
        else:
            result = 'customer: {} relation exist'.format(user_mobile)

    except Exception as e:
        result = 'customer not exist'
    logger.info('bind_customer: {}'.format(result))
    return result


@api_view(['POST'])
@permission_classes((AllowAny,))
def bind_customer(request):
    """销售绑定客户"""

    user_mobile = request.data.get('user_mobile')
    seller_mobile = request.data.get('seller_mobile')
    store_code = request.data.get('store_code')
    user_name = request.data.get('user_name')
    result = bind_relation(user_mobile, seller_mobile, user_name, store_code)
    logger.info('bind_customer: {}'.format(request.data))
    return ResInfo(result)
