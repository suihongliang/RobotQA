from rest_framework.permissions import AllowAny
from datetime import date

from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    UserBehavior,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
    QRCode)
from ..discount.models import (
    CoinRule,
    UserCoinRecord,
    Coupon,
    SendCoupon,
    CoinQRCode,
    )
from rest_framework import mixins
from rest_framework import viewsets
# from rest_framework.permissions import (
#     IsAuthenticated,
#     AllowAny,
#     )
from ..core.views import (
    CompanyFilterViewSet,
    SellerFilterViewSet,
    custom_permission,
    )
# from django.http import Http404
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
# from django.http import Http404
from .serializers import (
    BackendPermissionSerializer,
    BackendUserInfoSerializer,
    UserInfoDetailSerializer,
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
    UserBehaviorSerializer,
    QRCodeSerializer,
    CoinQRCodeSerializer,
)
from django_filters import rest_framework as filters
from django.http import Http404, HttpResponseRedirect


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
            if self.request.user.is_authenticated and user.role:
                queryset = user.role.permissions.all()

                page = self.paginate_queryset(queryset)

                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        return Response({
            'results': []
        })


class BackendRoleViewSet(CompanyFilterViewSet,
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
        'partial_update': [
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
    filterset_fields = ('is_seller',)


class BackendUserViewSet(CompanyFilterViewSet,
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
        'partial_update': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = BackendUser.objects.filter(
        is_superuser=False, is_staff=False).order_by('created')
    serializer_class = BackendUserSerializer
    filterset_fields = ('role__is_seller', 'mobile',)
    lookup_url_kwarg = 'mobile'
    lookup_field = 'mobile'


class UserInfoFilter(filters.FilterSet):
    min_age = filters.NumberFilter(
        field_name="age", lookup_expr='gte',
        help_text='年龄')
    max_age = filters.NumberFilter(
        field_name="age", lookup_expr='lte')
    min_created = filters.DateTimeFilter(
        field_name="created", lookup_expr='gte',
        help_text='创建时间')
    max_created = filters.DateTimeFilter(
        field_name="created", lookup_expr='lte')
    min_spend_coin = filters.NumberFilter(
        field_name="spend_coin", lookup_expr='gte',
        help_text='花费积分')
    max_spend_coin = filters.NumberFilter(
        field_name="spend_coin", lookup_expr='lte')
    min_last_active_time = filters.DateTimeFilter(
        field_name="last_active_time", lookup_expr='gte',
        help_text='上次到访时间')
    max_last_active_time = filters.DateTimeFilter(
        field_name="last_active_time", lookup_expr='lte')
    min_access_times = filters.NumberFilter(
        field_name="access_times", lookup_expr='gte',
        help_text='访问次数')
    max_access_times = filters.NumberFilter(
        field_name="access_times", lookup_expr='lte')
    min_coin = filters.NumberFilter(
        field_name="spend_coin", lookup_expr='gte',
        help_text='积分')
    max_coin = filters.NumberFilter(
        field_name="coin", lookup_expr='lte')

    class Meta:
        model = UserInfo
        fields = (
            'min_age', 'max_age', 'name', 'gender',
            'status', 'willingness', 'net_worth',
            'is_seller', 'customerrelation__seller__user__mobile',
            'min_created', 'max_created',
            'max_spend_coin', 'min_spend_coin',
            'min_last_active_time', 'max_last_active_time',
            'min_access_times', 'max_access_times',
            'min_coin', 'max_coin', 'customerrelation__seller')


class UserInfoViewSet(CompanyFilterViewSet,
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
            'customer_m',
        ],
        'retrieve': [
            'customer_m',
        ],
        'gender_list': [
            'customer_m',
        ],
        'status_list': [
            'customer_m',
        ],
        'update': [
            'customer_m',
        ],
        'partial_update': [
            'customer_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    filterset_class = UserInfoFilter
    # filterset_fields = (
    #     'name', 'gender', 'status', 'willingness', 'net_worth',
    #     'is_seller', 'customerrelation__seller__user__mobile',
    #     'age')
    ordering = ('created', 'gender', 'name',)

    queryset = UserInfo.objects.prefetch_related(
        'customerrelation', 'user').order_by('created')
    # serializer_class = UserInfoSerializer
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'
    companyfilter_field = 'user__company_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserInfoDetailSerializer
        return BackendUserInfoSerializer

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
            company_id = self.get_param_company_id()
            create = self.request.query_params.get('create')
            if create and company_id:
                b_user = BaseUser.objects.create(
                    company_id=company_id,
                    mobile=self.kwargs[lookup_url_kwarg])
                obj = b_user.userinfo
            else:
                raise Http404()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class UserOnlineOrderViewSet(CompanyFilterViewSet,
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

    c_perms = {
        'list': [
            'order_m',
        ],
        'retrieve': [
            'order_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )
    filterset_fields = ('location',)
    companyfilter_field = 'user__user__company_id'

    queryset = UserOnlineOrder.objects.order_by('created')
    serializer_class = UserOnlineOrderSerializer
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'


class SellerViewSet(CompanyFilterViewSet,
                    mixins.RetrieveModelMixin,
                    # mixins.UpdateModelMixin,
                    # mixins.CreateModelMixin,
                    mixins.ListModelMixin,):
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
        'partial_update': [
            'system_m',
        ],
        'update_seller': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )
    companyfilter_field = 'user__company_id'

    queryset = Seller.objects.order_by('created')
    serializer_class = SellerSerializer
    # filterset_fields = ('name',)
    lookup_url_kwarg = 'user__mobile'
    lookup_field = 'user__mobile'

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSellerSerializer
        elif self.action == 'update_seller':
            return UpdateSellerSerializer
        return SellerSerializer

    # @action(methods=['patch'], url_path='seller-config', detail=True)
    # def update_seller(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     is_seller = request.data.get('is_seller', True)
    #     instance.user.userinfo.is_seller = is_seller
    #     instance.user.userinfo.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


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

    c_perms = {
        'list': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
        'partial_update': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )
    companyfilter_field = 'user__user__company_id'

    queryset = CustomerRelation.objects.order_by('created')
    serializer_class = CustomerRelationSerializer
    filterset_fields = (
        'user__user__mobile',
        'seller__user__mobile',
        'mark_name',
    )
    userfilter_field = 'seller__user__mobile'
    ordering = ('created',)
    lookup_url_kwarg = 'user__user__mobile'
    lookup_field = 'user__user__mobile'


class CoinRuleViewSet(CompanyFilterViewSet,
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

    c_perms = {
        'list': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
        'partial_update': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = CoinRule.objects.order_by('category')
    serializer_class = CoinRuleSerializer
    filterset_fields = ('company_id', 'category',)


class UserCoinRecordViewSet(CompanyFilterViewSet,
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

    c_perms = {
        'list': [
            'coin_m',
        ],
        'create': [
            'coin_m',
        ],
        'retrieve': [
            'coin_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = UserCoinRecord.objects.order_by('id')
    serializer_class = UserCoinRecordSerializer
    filterset_fields = ('rule',)
    filterset_fields = (
        'user__user__mobile',
    )
    companyfilter_field = 'user__user__company_id'


class CouponViewSet(CompanyFilterViewSet,
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

    c_perms = {
        'list': [
            'system_m',
        ],
        'create': [
            'system_m',
        ],
        'retrieve': [
            'system_m',
        ],
        'destroy': [
            'system_m',
        ],
        'update': [
            'system_m',
        ],
        'partial_update': [
            'system_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = Coupon.objects.order_by('id')
    serializer_class = CouponSerializer
    filterset_fields = ('is_active',)
    companyfilter_field = 'company_id'


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

    c_perms = {
        'list': [
            'coin_m',
        ],
        'create': [
            'coin_m',
        ],
        'retrieve': [
            'coin_m',
        ],
        'update': [
            'coin_m',
        ],
        'partial_update': [
            'coin_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = SendCoupon.objects.order_by('id')
    serializer_class = SendCouponSerializer
    filterset_fields = ('coupon__is_active', 'user__user__mobile')
    companyfilter_field = 'user__user__company_id'
    userfilter_field = 'backenduser__mobile'


class UserBehaviorViewSet(CompanyFilterViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,):
    c_perms = {
        # 'list': [
        #     'forbiden',
        # ],
        # 'create': [
        #     'forbiden',
        # ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    class UserBehaviorFilter(filters.FilterSet):
        min_created_time = filters.DateTimeFilter(
            field_name="created", lookup_expr='gte',
            help_text='创建时间')
        max_created_time = filters.DateTimeFilter(
            field_name="created", lookup_expr='lte')

        class Meta:
            model = UserBehavior
            fields = ['user__mobile', 'min_created_time', 'max_created_time']

    queryset = UserBehavior.objects.order_by('id')
    serializer_class = UserBehaviorSerializer
    companyfilter_field = 'user__company_id'
    filter_class = UserBehaviorFilter


class QRCodeViewSet(CompanyFilterViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin):
    c_perms = {
        'list': [
            'coin_m',
        ],
        'create': [
            'coin_m',
        ],
        'retrieve': [
            'coin_m',
        ],
        'update': [
            'coin_m',
        ],
        'partial_update': [
            'coin_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = QRCode.objects.order_by('-id')
    serializer_class = QRCodeSerializer
    filterset_fields = ('company_id',)
    companyfilter_field = 'company_id'


class CoinQRCodeViewSet(CompanyFilterViewSet,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin):
    c_perms = {
        'list': [
            'coin_m',
        ],
        'create': [
            'coin_m',
        ],
        'retrieve': [
            'coin_m',
        ],
        'update': [
            'coin_m',
        ],
        'partial_update': [
            'coin_m',
        ],
    }
    permission_classes = (
        # AllowAny,
        custom_permission(c_perms),
    )

    queryset = CoinQRCode.objects.order_by('-id')
    serializer_class = CoinQRCodeSerializer
    filterset_fields = ('company_id',)
    companyfilter_field = 'company_id'


@api_view(['GET'])
def sdvr(request):
    mobile = request.GET.get('mobile')
    user = BaseUser.objects.filter(mobile=mobile).first()
    if user:
        UserBehavior.objects.create(user_id=user.id,
                                    category='3dvr',
                                    location='')
        rule = CoinRule.objects.filter(category=3).first()
        UserCoinRecord.objects.get_or_create(
            user_id=user.id,
            rule=rule,
            created__date=date.today(), defaults={
                'coin': rule.coin, 'update_status': True, 'extra_data': {}})
    return HttpResponseRedirect(
        "https://beyond.3dnest.cn/house/?m=shhzhb_xykjly_62&from=groupmessage/")  # noqa
