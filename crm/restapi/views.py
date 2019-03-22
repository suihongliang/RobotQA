from ..user.models import (
    UserInfo,
    UserOnlineOrder,
    )
from ..sale.models import (
    Seller,
    )
from ..discount.models import (
    CoinRule,
    UserCoinRecord,
    )
from rest_framework import viewsets, mixins
from rest_framework.permissions import (
    # IsAuthenticated,
    AllowAny,
    )
# from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.http import Http404
from .serializers import (
    UserInfoSerializer,
    UserOnlineOrderSerializer,
    SellerSerializer,
    CreateSellerSerializer,
    UpdateSellerSerializer,
    CoinRuleSerializer,
    UserCoinRecordSerializer,
    )

# Create your views here.


class UserInfoViewSet(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin):
    '''
    retrieve:
        获取用户详情
        ---

    list:
        获取用户列表
        ---

    update:
        更新用户信息
        ---
    '''

    permission_classes = (
        AllowAny,
    )
    filterset_fields = (
        'name', 'gender', 'status', 'willingness', 'net_worth',)
    ordering = ('created', 'gender', 'name',)

    queryset = UserInfo.objects.order_by('created')
    serializer_class = UserInfoSerializer
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'


class UserOnlineOrderViewSet(viewsets.GenericViewSet,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,):
    '''
    retrieve:
        获取点单详情
        ---

    list:
        获取点单列表
        ---
    '''

    permission_classes = (
        AllowAny,
    )
    filterset_fields = ('location',)

    queryset = UserOnlineOrder.objects.order_by('created')
    serializer_class = UserOnlineOrderSerializer
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'


class SellerViewSet(viewsets.GenericViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin):
    '''
    retrieve:
        获取销售详情
        ---

    list:
        获取销售列表
        ---

    create:
        创建销售
        ---

    update:
        更改销售信息
        ---

    update_seller:
        启用禁用销售
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = Seller.objects.order_by('created')
    serializer_class = SellerSerializer
    filterset_fields = ('name',)
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSellerSerializer
        elif self.action == 'update_seller':
            return UpdateSellerSerializer
        return SellerSerializer

    @action(methods=['patch'], url_path='seller-config', detail=True)
    def update_seller(self, request, *args, **kwargs):
        instance = self.get_object()
        is_seller = request.data.get('is_seller', True)
        instance.user.userinfo.is_seller = is_seller
        instance.user.userinfo.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CoinRuleViewSet(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin):
    '''
    retrieve:
        获取积分规则详情
        ---

    list:
        获取积分规则列表
        ---

    update:
        更新积分规则可领取积分
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = CoinRule.objects.order_by('category')
    serializer_class = CoinRuleSerializer
    filterset_fields = ('store_code', 'category',)


class UserCoinRecordViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    '''
    retrieve:
        获取积分规则详情
        ---

    list:
        获取积分规则列表
        ---

    create:
        用户领取积分
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = UserCoinRecord.objects.order_by('id')
    serializer_class = UserCoinRecordSerializer
    filterset_fields = ('rule',)
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'
