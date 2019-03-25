from ..user.models import (
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
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
from ..core.views import (
    StoreFilterMixin,
    SellerFilterMixin,
    )
# from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.http import Http404
from .serializers import (
    BackendPermissionSerializer,
    UserInfoSerializer,
    UserOnlineOrderSerializer,
    SellerSerializer,
    CreateSellerSerializer,
    UpdateSellerSerializer,
    CoinRuleSerializer,
    UserCoinRecordSerializer,
    BackendRoleSerializer,
    CustomerRelationSerializer,
    )

# Create your views here.


class ChoicesViewMixin():

    def get_choice_data(self, model, field):
        return {'results': [
            {
                'key': key,
                'name': name,
            }
            for key, name in model._meta.get_field(field).choices
        ]}


class BackendPermissionViewSet(viewsets.GenericViewSet,
                               StoreFilterMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,):
    '''
    list:
        获取权限列表
        ---
    '''
    permission_classes = (
        AllowAny,
    )

    queryset = BackendPermission.objects.order_by('id')
    serializer_class = BackendPermissionSerializer


class BackendRoleViewSet(viewsets.GenericViewSet,
                         StoreFilterMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,):
    '''
    list:
        获取权限列表
        ---
    '''
    permission_classes = (
        AllowAny,
    )

    queryset = BackendRole.objects.order_by('created')
    serializer_class = BackendRoleSerializer


class UserInfoViewSet(viewsets.GenericViewSet,
                      StoreFilterMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      ChoicesViewMixin):
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

    gender_list:
        选项列表
        ---

    status_list:
        选项列表
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
    storefilter_field = 'user__store_code'

    @action(methods=['get'], url_path='list/gender', detail=False)
    def gender_list(self, request, *args, **kwargs):
        return Response(self.get_choice_data(UserInfo, 'gender'))

    @action(methods=['get'], url_path='list/status', detail=False)
    def status_list(self, request, *args, **kwargs):
        return Response(self.get_choice_data(UserInfo, 'status'))


class UserOnlineOrderViewSet(viewsets.GenericViewSet,
                             StoreFilterMixin,
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
    storefilter_field = 'user__user__store_code'

    queryset = UserOnlineOrder.objects.order_by('created')
    serializer_class = UserOnlineOrderSerializer
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'


class SellerViewSet(viewsets.GenericViewSet,
                    StoreFilterMixin,
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
    storefilter_field = 'user__store_code'

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


class CustomerRelationViewSet(viewsets.GenericViewSet,
                              StoreFilterMixin,
                              SellerFilterMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin):
    '''
    list:
        获取客户关系列表
        ---

    create:
        创建客户关系
        ---

    update:
        更改客户关系信息
        ---
    '''

    permission_classes = (
        AllowAny,
    )
    storefilter_field = 'seller__user__store_code'

    queryset = CustomerRelation.objects.order_by('created')
    serializer_class = CustomerRelationSerializer
    filterset_fields = (
        'is_delete',
        'user__user__mobile',
        'seller__user__mobile',
    )
    ordering = ('created',)


class CoinRuleViewSet(viewsets.GenericViewSet,
                      StoreFilterMixin,
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
                            StoreFilterMixin,
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
    storefilter_field = 'user__user__store_code'
