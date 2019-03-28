import logging
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

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

    permission_classes = (AllowAny,)

    def list(self, request):
        """
            门店商品列表
            store=C0001&name= &barcode=
        """
        params = request.query_params.dict()
        # params['store'] = request.user.store
        params['store'] = 'C0001'
        res = requests.get(settings.ERP_JIAN24_URL + '/crm/product/', params=params)
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
        res = requests.post(settings.ERP_JIAN24_URL + '/crm/product/', json=data)
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
        res = requests.put(settings.ERP_JIAN24_URL + '/merchant/store-product/{0}/'.format(pk), json=data)
        return Response(res.json())

    @action(detail=False)
    def check_barcode(self, request):
        """
            check barcode存在
            barcode=6920152400777
        """
        params = request.query_params.dict()
        res = requests.get(settings.ERP_JIAN24_URL + '/crm/product/check_barcode/', params=params)
        return Response(res.json())
