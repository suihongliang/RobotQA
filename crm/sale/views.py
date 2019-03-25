from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from crm.sale.models import Seller, CustomerRelation
from crm.user.models import UserInfo, BaseUser


def bind_relation(user_mobile, seller_mobile, store_code, user_name):
    from crm.sale.models import CustomerRelation
    try:
        user = UserInfo.objects.get(user__mobile=user_mobile,
                                    user__store_code=store_code,
                                    )
        seller = Seller.objects.get(user__mobile=seller_mobile,
                                    user__store_code=store_code,
                                    )
        relation, created = CustomerRelation.objects.get_or_create(seller=seller, user=user)

        if created:
            user.name = user_name
            user.save(update_fields=['name'])
            result = {'msg': 'add customer success'}
        else:
            result = {'msg': 'customer relation exist'}

    except Exception as e:
        result = {'msg': 'customer not exist'}

    return result


@api_view(['POST'])
@permission_classes((AllowAny,))
def bind_customer(request):
    """销售绑定客户"""
    user_mobile = request.data.get('user_mobile')
    seller_mobile = request.data.get('seller_mobile')
    store_code = request.data.get('store_code')
    user_name = request.data.get('user_name', '')
    result = bind_relation(user_mobile, seller_mobile, store_code, user_name)

    return Response(result)
