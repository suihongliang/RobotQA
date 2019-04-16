from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.permissions import AllowAny
from datetime import date, datetime
from django.conf import settings

from crm.core.utils import week_date_range
from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    UserBehavior,
    BackendGroup,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
    QRCode)
from ..discount.models import (
    CoinRule,
    Coupon,
    SendCoupon,
    CoinQRCode,
    PointRecord)
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
    IsOwnerOrReadOnly,
    )
# from django.http import Http404
from rest_framework.decorators import action, api_view, permission_classes
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
    BackendRoleSerializer,
    BackendUserSerializer,
    CustomerRelationSerializer,
    CouponSerializer,
    SendCouponSerializer,
    UserBehaviorSerializer,
    QRCodeSerializer,
    CoinQRCodeSerializer,
    BackendGroupSerializer,
    BackendGroupDetailSerializer,
    UserInfoReportSerializer, PointRecordSerializer, CreatePointRecordSerializer)
from django_filters import rest_framework as filters
from django.http import Http404, HttpResponseRedirect, HttpResponse


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


class BackendGroupViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet,):
    '''
    list:
        获取后台组列表
        ---

    create:
        创建后台组
        ---

    retrieve:
        获取后台组详情
        ---

    update:
        更新后台组
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

    queryset = BackendGroup.objects.order_by('id')
    serializer_class = BackendGroupSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BackendGroupDetailSerializer
        return BackendGroupSerializer


class BackendUserViewSet(SellerFilterViewSet,
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
            'system_m', 'system_m_read'
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

    class BackendUserFilter(filters.FilterSet):
        has_group = filters.BooleanFilter(
            field_name="group", lookup_expr='isnull')
        group_in = filters.BaseInFilter(
            field_name="group_id", lookup_expr='in')

        class Meta:
            model = BackendUser
            fields = ['role__is_seller', 'mobile', 'has_group',
                      'group_id', 'group_in', 'role__name']

    queryset = BackendUser.objects.filter(
        is_superuser=False, is_staff=False).order_by('created')
    serializer_class = BackendUserSerializer
    # filterset_fields = ('role__is_seller', 'mobile',)
    filterset_class = BackendUserFilter
    lookup_url_kwarg = 'mobile'
    lookup_field = 'mobile'
    pagination_class = []


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
        field_name="coin", lookup_expr='gte',
        help_text='积分')
    max_coin = filters.NumberFilter(
        field_name="coin", lookup_expr='lte')
    unbind_seller = filters.BooleanFilter(
        field_name="customerrelation__seller", lookup_expr='isnull',
        help_text='未绑定销售')
    min_bind_time = filters.DateTimeFilter(
        field_name="customerrelation__created", lookup_expr='gte',
        help_text='绑定时间')
    max_bind_time = filters.DateTimeFilter(
        field_name="customerrelation__created", lookup_expr='lte',)
    min_sampleroom_times = filters.NumberFilter(
        field_name="sampleroom_times", lookup_expr='gte',
        help_text='最少看样板房次数')
    max_sampleroom_times = filters.NumberFilter(
        field_name="sampleroom_times", lookup_expr='lte',
        help_text="最大看样板房次数")
    min_sampleroom_seconds = filters.NumberFilter(
        field_name="sampleroom_seconds", lookup_expr='gte',
        help_text='最少看样板房总停留秒数')
    max_sampleroom_seconds = filters.NumberFilter(
        field_name="sampleroom_seconds", lookup_expr='lte',
        help_text="最大看样板房总停留秒数")
    min_sdver_times = filters.NumberFilter(
        field_name="sdver_times", lookup_expr='gte',
        help_text='最少3DVR看房次数')
    max_sdver_times = filters.NumberFilter(
        field_name="sdver_times", lookup_expr='lte',
        help_text="最多3DVR看房次数")

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
            'min_coin', 'max_coin', 'customerrelation__seller',
            'user__mobile', 'unbind_seller', 'min_bind_time',
            'max_bind_time', 'min_sampleroom_times', 'max_sampleroom_times',
            'min_sampleroom_seconds', 'max_sampleroom_seconds', 'min_sdver_times', 'max_sdver_times')


class UserInfoViewSet(SellerFilterViewSet,
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
        custom_permission(c_perms), IsOwnerOrReadOnly
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
    userfilter_field = 'customerrelation__seller__user__mobile'

    def get_queryset(self):
        queryset = super().get_queryset()
        is_sampleroom = self.request.GET.get('is_sampleroom')
        if is_sampleroom == 'true':
            queryset = queryset.select_related('user').filter(
                user__userbehavior__category='sampleroom').distinct()
        elif is_sampleroom == 'false':
            queryset = queryset.select_related('user').exclude(
                user__userbehavior__category='sampleroom')
        return queryset

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

class UserInfoReportViewSet(UserInfoViewSet):
    def get_serializer_class(self):
        return UserInfoReportSerializer


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


class CustomerRelationFilter(filters.FilterSet):
    mark_name = filters.CharFilter(
        field_name="mark_name", lookup_expr='icontains',
        help_text='备注名'
    )
    user__user__mobile = filters.CharFilter(
        field_name="user__user__mobile", lookup_expr='icontains',
        help_text='客户手机'
    )

    class Meta:
        model = CustomerRelation
        fields = (
            'user__user__mobile', 'seller__user__mobile', 'mark_name',
        )


class CustomerRelationViewSet(CompanyFilterViewSet,
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
    # filterset_fields = (
    #     'user__user__mobile',
    #     'seller__user__mobile',
    #     'mark_name',
    # )
    userfilter_field = 'seller__user__mobile'
    ordering = ('-created',)
    lookup_url_kwarg = 'user__user__mobile'
    lookup_field = 'user__user__mobile'
    filterset_class = CustomerRelationFilter


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
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin):
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

    queryset = PointRecord.objects.order_by('id')
    serializer_class = PointRecordSerializer
    filterset_fields = ('rule',)
    filterset_fields = (
        'user__user__mobile',
        'change_type',
        'order_no',
        'seller__mobile',
        'rule__category'
    )
    companyfilter_field = 'user__user__company_id'

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePointRecordSerializer

        return PointRecordSerializer


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
            'system_m', 'coin_m',
        ],
        'create': [
            'system_m', 'coin_m',
        ],
        'retrieve': [
            'system_m', 'coin_m',
        ],
        'destroy': [
            'system_m', 'coin_m',
        ],
        'update': [
            'system_m', 'coin_m',
        ],
        'partial_update': [
            'system_m', 'coin_m',
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
            fields = ['user__mobile', 'min_created_time', 'max_created_time', 'category',
                      'user__userinfo__is_seller',
                      ]

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
@permission_classes((AllowAny, ))
def sdvr(request):
    mobile = request.GET.get('mobile')
    user = UserInfo.objects.filter(user__mobile=mobile).first()
    if user:
        UserBehavior.objects.create(user_id=user.user_id,
                                    category='3dvr',
                                    location='')
        user.sdver_times += 1
        user.save()
        rule = CoinRule.objects.filter(category=3).first()
        start_at, end_at = week_date_range()
        PointRecord.objects.get_or_create(
            user_id=user.user_id,
            rule=rule,
            created_at__date__gte=start_at,
            created_at__date__lte=end_at,
            defaults={'coin': rule.coin, 'change_type': 'rule_reward'})

    return HttpResponseRedirect(settings.SD_URL)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def message(request):
    mobile = request.GET.get('mobile')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    user = BaseUser.objects.filter(mobile=mobile).first()
    record_list = PointRecord.objects.filter(user_id=user.id if user else None).order_by('-id')

    paginator = Paginator(record_list.all(), limit)
    try:
        limit_values = paginator.page(page)
    except PageNotAnInteger:
        limit_values = paginator.page(1)
    except EmptyPage:
        limit_values = paginator.page(paginator.num_pages)
    ret = []
    for record in limit_values:
        change_name = record.get_change_type_display()
        change_by = record.change_by
        ret.append({'coin': record.coin,
                    'created': str(record.created_at),
                    'change_name': change_name,
                    'change_by': change_by})
    if user:
        UserInfo.objects.filter(user_id=user.id).update(**{'msg_last_at': datetime.now()})

    return Response({
        'data': ret,
        'page_size': limit,
        'current_page': page,
        'total_size': record_list.count(),
        'total_pages': paginator.num_pages})
