import urllib
import json
import requests
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from crm.core.views import SellerFilterViewSet
from crm.user.models import UserInfo


class OrderViewSet(SellerFilterViewSet):
    """
    门店订单查询
    ---
    list:
        门店订单列表
    retrieve:
        门店订单详情

    """

    permission_classes = (AllowAny,)
    queryset = UserInfo.objects.prefetch_related(
        'customerrelation', 'user').order_by('created')
    companyfilter_field = 'user__company_id'
    userfilter_field = 'customerrelation__seller__user__mobile'

    def customer_filter(self, params):
        if self.request.user.is_authenticated:
            if self.request.user.role:
                if self.request.user.role.only_myself:
                    queryset = self.get_queryset()
                    if params.get('mobile'):
                        queryset = queryset.filter(user__mobile=params['mobile'])
                    mobile_list = queryset.values_list('user__mobile', flat=True)
                    params['mobile_list'] = json.dumps(list(mobile_list))
        return params

    def list(self, request):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        params = self.customer_filter(params)
        mobile_list = params.get('mobile_list')
        if mobile_list == '[]':
            return Response({"code": 200, "data": []})
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order', params=params)
        return Response(result.json())

    def retrieve(self, request, pk):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        result = requests.get(settings.ERP_JIAN24_URL + '/merchant/order-detail/{0}'.format(pk), params=params)
        return Response(result.json())

    @list_route()
    def export(self, request):
        query_string = request.META['QUERY_STRING']
        params = dict(urllib.parse.parse_qsl(query_string))
        params = self.customer_filter(params)
        mobile_list = params.get('mobile_list')
        if mobile_list == '[]':
            return Response({"code": 200, "data": []})
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
