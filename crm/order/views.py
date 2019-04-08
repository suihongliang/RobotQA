import urllib

import requests
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import list_route
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
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order', params=params)
        return Response(result.json())

    def retrieve(self, request, pk):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order-detail/{0}'.format(pk), params=params)
        return Response(result.json())


class OrderViewSetExport(ViewSet):
    permission_classes = (AllowAny,)

    @list_route()
    def export(self, request):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        response = HttpResponse(content_type='application/vnd.ms-excel')
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order/crm_export/', params=params)
        response.write(result.content)
        response['Content-Disposition'] = 'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('订单列表'))
        return response

    @list_route()
    def export_detail(self, request):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        response = HttpResponse(content_type='application/vnd.ms-excel')
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order/export_detail/', params=params)
        response.write(result.content)
        response['Content-Disposition'] = 'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('订单明细列表'))
        return response
