import urllib

import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet


class OrderViewSet(ViewSet):
    """
    门店订单查询
    ---
    list:
        门店订单列表
    retrieve:
        门店订单详情

    """

    permission_classes = (AllowAny,)

    def list(self, request):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        params['store_code_havings'] = 'C0001'
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order', params=params)
        return Response(result.json())

    def retrieve(self, request, pk):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        params = {'store_code_havings': 'C0001'}
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order-detail/{0}'.format(pk), params=params)
        return Response(result.json())
