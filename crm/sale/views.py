from rest_framework.decorators import api_view, permission_classes
from crm.sale.models import Seller, CustomerRelation
from crm.user.models import UserBehavior
from rest_framework.response import Response


@api_view()
@permission_classes([])
def scan_bind_seller(request):
    code = request.GET.get('code')
    mobile_customer = request.GET.get('mobile_customer')
    customer_relation = CustomerRelation.objects.get(user__user__mobile=mobile_customer)
    if customer_relation.seller:
        msg = '已绑定销售'
        return Response(msg)
    seller = Seller.objects.filter(qrcode__code=code)
    if not seller.exists():
        msg = '二维码没有关联的销售'
        return Response(msg)
    customer_relation.seller = seller[0]
    customer_relation.mark_name = mobile_customer
    customer_relation.save(update_fields=['seller', 'mark_name'])
    msg = '绑定成功'
    return Response(msg)
