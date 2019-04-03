import logging
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from crm.core.views import custom_permission
from crm.user.utils import generate_sign

logger = logging.getLogger('product_logger')


class StoreProductViewSet(ViewSet):
    """
    商品管理
    ---
    list:
        门店商品列表

    update:
        商品编辑
    """
    c_perms = {
        'list': [
            'product_m',
        ],
        'retrieve': [
            'product_m',
        ],
        'create': [
            'product_m',
        ],
        'update': [
            'product_m',
        ],
        'partial_update': [
            'product_m',
        ],
    }
    permission_classes = (
        custom_permission(c_perms, ),
    )

    def list(self, request):
        """
            门店商品列表
            store=C0001&name= &barcode=
        """
        params = request.query_params.dict()
        params['company_id'] = request.user.company_id
        sign = generate_sign(params)
        params['sign'] = sign
        res = requests.get(
            settings.ERP_JIAN24_URL + '/crm/product/', params=params)
        return Response(res.json())

    def create(self, request):
        """
            商品新增
            {
                "store":"C0001",
                "barcode":"667",
                "name":"666",
                "price":"666",
                "weight":"666"
            }
        """

        data = request.data
        sign = generate_sign(data, 'POST')
        params = dict(
            sign=sign,
            company_id=request.user.company_id,
        )
        res = requests.post(
            settings.ERP_JIAN24_URL + '/crm/product/',
            json=data, params=params)
        return Response(res.json())

    def update(self, request, pk):
        """
            商品编辑
            {
                "price":20,
                "weight":100
            }
        """
        data = request.data
        sign = generate_sign(data, 'PUT')
        params = dict(
            sign=sign,
            company_id=request.user.company_id,
        )
        res = requests.put(
            settings.ERP_JIAN24_URL + '/crm/product/{0}/'.format(pk),
            json=data, params=params)
        return Response(res.json())

    @action(detail=False)
    def check_barcode(self, request):
        """
            check barcode存在
            barcode=6920152400777
        """
        params = request.query_params.dict()
        sign = generate_sign(params)
        params['sign'] = sign
        res = requests.get(
            settings.ERP_JIAN24_URL + '/crm/product/check_barcode/',
            params=params)
        return Response(res.json())

    @action(detail=False)
    def get_company_store(self, request):
        params = request.query_params.dict()
        sign = generate_sign(params)
        params['sign'] = sign
        res = requests.get(
            settings.ERP_JIAN24_URL + '/crm/get-company-store/', params=params)
        return Response(res.json())
