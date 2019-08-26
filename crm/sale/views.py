from rest_framework.decorators import api_view, permission_classes

from crm.discount.models import CoinRule, PointRecord
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
    user, create = BaseUser.objects.get_or_create(mobile=mobile_customer, company_id=company_id)
    customer_relation = CustomerRelation.objects.get(
        user__user__mobile=mobile_customer, user__user__company_id=company_id)
    if customer_relation.seller:
        msg = dict(msg='已绑定销售', code=400)
        return Response(msg)
    seller = Seller.objects.filter(qrcode__code=code, user__company_id=company_id)
    if not seller.exists():
        msg = dict(msg='二维码没有关联的销售', code=400)
        return Response(msg)
    if customer_relation.user.mobile == seller[0].mobile:
        msg = dict(msg='不能绑定自己', code=400)
        return Response(msg)
    customer_relation.seller = seller[0]
    customer_relation.created = timezone.now()
    customer_relation.save(update_fields=['seller', 'created'])
    customer_relation.user.status = 3
    customer_relation.user.save()
    msg = dict(msg='绑定成功', code=200)

    UserBehavior.objects.create(user_id=customer_relation.user_id,
                                category='sellerbind',
                                location='')
    rule = CoinRule.objects.filter(company_id=company_id, category=6).first()
    if rule:
        PointRecord.objects.create(user_id=customer_relation.user_id,
                                   rule=rule,
                                   coin=rule.coin,
                                   change_type='rule_reward')
    return Response(msg)


from rest_framework.views import APIView
from crm.core.utils import CustomPagination
from crm.user.models import UserBehavior
from crm.sale.serializes import MatchFaceSerialize
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView


@api_view()
@permission_classes([])
def match_face(request):
    """
    人脸匹配报告
    :param request:
    :return:
    """
    return Response({'msg': 'success'})
    pass


class MatchFace(APIView):
    """人脸匹配报告"""
    print('hello world')

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 20)
        min_create_datetime = request.GET.get('min_create_datetime', None)
        max_create_datetime = request.GET.get('max_create_datetime', None)
        queryset = UserBehavior.objects.values('user__userinfo__name',
                                               'user__mobile', 'created',
                                               'lib_image_url',
                                               'face_image_url', 'result')

        print(queryset)
        bs = MatchFaceSerialize(queryset, many=True)

        # return Response({'msg': 'success'})
        return Response(bs.data)
