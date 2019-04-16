from rest_framework.decorators import api_view, permission_classes
from crm.sale.models import Seller, CustomerRelation
from crm.user.models import UserBehavior
from rest_framework.response import Response
from crm.user.models import BaseUser
from django.utils import timezone


@api_view()
@permission_classes([])
def scan_bind_seller(request):
    code = request.GET.get('code', '')
    mobile_customer = request.GET.get('mobile_customer')
    company_id = request.GET.get('company_id')
    user = BaseUser.objects.get_or_create(mobile=mobile_customer, defaults={'company_id': company_id})
    customer_relation = CustomerRelation.objects.get(
        user__user__mobile=mobile_customer)
    if customer_relation.seller:
        msg = dict(msg='已绑定销售', code=400)
        return Response(msg)
    seller = Seller.objects.filter(qrcode__code=code)
    if not seller.exists():
        msg = dict(msg='二维码没有关联的销售', code=400)
        return Response(msg)
    if customer_relation.user.mobile == seller[0].mobile:
        msg = dict(msg='不能绑定自己', code=400)
        return Response(msg)
    customer_relation.seller = seller[0]
    customer_relation.mark_name = mobile_customer
    customer_relation.created = timezone.now()
    customer_relation.save(update_fields=['seller', 'mark_name', 'created'])
    msg = dict(msg='绑定成功', code=200)

    UserBehavior.objects.create(user_id=customer_relation.user_id,
                                category='sellerbind',
                                location='')
    return Response(msg)
