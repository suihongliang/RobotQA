from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
    )
from ..discount.models import (
    CoinRule,
    UserCoinRecord,
    Coupon,
    SendCoupon,
    )
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import (
    # IsAuthenticated,
    AllowAny,
    )
from ..core.views import (
    StoreFilterViewSet,
    SellerFilterViewSet,
    custom_permission,
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
    BackendUserSerializer,
    CustomerRelationSerializer,
    CouponSerializer,
    SendCouponSerializer,
    )
from django.http import Http404

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
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,):
    '''
    list:
        获取权限列表
        ---

    myself_perms:
        获取我自己的权限
        ---
    '''
    c_perms = {
        'list': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
        'myself_perms': [],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = BackendPermission.objects.order_by('id')
    serializer_class = BackendPermissionSerializer

    @action(methods=['get'], url_path='myself', detail=False)
    def myself_perms(self, request, *args, **kwargs):
        if self.request.user:
            user = self.request.user
            if user.role:
                queryset = user.role.permissions.all()

                page = self.paginate_queryset(queryset)

                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        return Response({
            'results': []
        })


class BackendRoleViewSet(StoreFilterViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,):
    '''
    list:
        获取角色列表
        ---

    create:
        创建角色
        ---

    retrieve:
        获取角色详情
        ---

    update:
        更新角色
        ---

    destroy:
        删除角色
        ---
    '''
    c_perms = {
        'list': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
        'create': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
        'destroy': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = BackendRole.objects.order_by('created')
    serializer_class = BackendRoleSerializer


class BackendUserViewSet(StoreFilterViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,):
    '''
    list:
        获取后台登录用户列表
        ---
    '''
    c_perms = {
        'list': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
        'create': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = BackendUser.objects.filter(
        is_superuser=False, is_active=True, is_staff=False).order_by('created')
    serializer_class = BackendUserSerializer
    lookup_url_kwarg = 'mobile'
    lookup_field = 'mobile'


class UserInfoViewSet(StoreFilterViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      ChoicesViewMixin):
    '''
    retrieve:
        获取用户详情, 可以追加参数 create: 若不存在就创建
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

    c_perms = {
        'list': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
        'create': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
    }
    permission_classes = (
        AllowAny,
        # custom_permission(c_perms),
    )

    filterset_fields = (
        'name', 'gender', 'status', 'willingness', 'net_worth',
        'is_seller',)
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

    def get_object(self):
        '''
        处理自动创建用户
        '''
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.filter(**filter_kwargs).first()
        if not obj:
            store_code = self.get_param_store_code()
            create = self.request.query_params.get('create')
            if create and store_code:
                b_user = BaseUser.objects.create(
                    store_code=store_code,
                    mobile=self.kwargs[lookup_url_kwarg])
                obj = b_user.userinfo
            else:
                raise Http404()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class UserOnlineOrderViewSet(StoreFilterViewSet,
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


class SellerViewSet(StoreFilterViewSet,
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


class CustomerRelationViewSet(SellerFilterViewSet,
                              mixins.ListModelMixin,
                              mixins.UpdateModelMixin):
    '''
    list:
        获取客户关系列表
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
        'user__user__mobile',
        'seller__user__mobile',
    )
    userfilter_field = 'seller__user__mobile'
    ordering = ('created',)
    lookup_url_kwarg = 'user__user__mobile'
    lookup_field = 'user__user__mobile'


class CoinRuleViewSet(StoreFilterViewSet,
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


class UserCoinRecordViewSet(StoreFilterViewSet,
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


class CouponViewSet(StoreFilterViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,):
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

    queryset = Coupon.objects.order_by('id')
    serializer_class = CouponSerializer
    filterset_fields = ('is_active',)
    storefilter_field = 'store_code'


class SendCouponViewSet(SellerFilterViewSet,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,):
    '''
    retrieve:
        获取用户优惠券
        ---

    list:
        获取用户优惠券列表
        ---

    create:
        发送优惠券
        ---

    update:
        更新优惠券
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = SendCoupon.objects.order_by('id')
    serializer_class = SendCouponSerializer
    filterset_fields = ('coupon__is_active', 'user__user__mobile')
    storefilter_field = 'user__user__store_code'
    userfilter_field = 'backenduser__mobile'
