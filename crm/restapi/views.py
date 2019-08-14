import json
import requests

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.permissions import AllowAny
from datetime import date, datetime
from django.conf import settings
from django.contrib.auth import authenticate

from crm.core.utils import website_config

from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    UserBehavior,
    BackendGroup,
    UserDailyData,
    SubTitle,
    SubTitleRecord,
    SubTitleChoice,
    VR)
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
    UserInfoReportSerializer, PointRecordSerializer, CreatePointRecordSerializer, UserDailyDataSerializer)
from django_filters import rest_framework as filters
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse

import time
import base64
import hmac
from hashlib import sha1 as sha
from django.http import HttpResponse
import urllib.request
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
import urllib.parse


# Create your views here.

def cores(data, status=200):
    resp = Response(data, status=status)
    if settings.DEBUG:
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        resp[
            "Access-Control-Allow-Headers"] = "Access-Control-Allow-Methods,Origin, Accept，Content-Type, Access-Control-Allow-Origin, access-control-allow-headers,Authorization, X-Requested-With"

    return resp


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

                resp = self.get_paginated_response(serializer.data)
                resp.data["config"] = website_config(request)
                return resp
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


class BackendGroupViewSet(CompanyFilterViewSet,
                          mixins.RetrieveModelMixin,
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
    companyfilter_field = 'manager__company_id'

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
        no_group = filters.BooleanFilter(
            field_name="group", lookup_expr='isnull')
        group_in = filters.BaseInFilter(
            field_name="group_id", lookup_expr='in')
        is_active = filters.BooleanFilter(
            field_name="is_active", help_text="是否禁用"
        )

        class Meta:
            model = BackendUser
            fields = ['role__is_seller', 'mobile', 'no_group',
                      'group_id', 'group_in', 'role__name', 'is_active']

    # queryset = BackendUser.objects.filter(
    #     is_superuser=False, is_staff=False).order_by('created')
    queryset = BackendUser.objects.order_by('created')
    serializer_class = BackendUserSerializer
    # filterset_fields = ('role__is_seller', 'mobile',)
    filterset_class = BackendUserFilter
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
    min_microstore_times = filters.NumberFilter(
        field_name="microstore_times", lookup_expr='gte',
        help_text='最少小店次数')
    max_microstore_times = filters.NumberFilter(
        field_name="microstore_times", lookup_expr='lte',
        help_text="最大小店次数")
    min_microstore_seconds = filters.NumberFilter(
        field_name="microstore_seconds", lookup_expr='gte',
        help_text='最少小店总停留秒数')
    max_microstore_seconds = filters.NumberFilter(
        field_name="microstore_seconds", lookup_expr='lte',
        help_text="最大小店总停留秒数")
    min_big_room_seconds = filters.NumberFilter(
        field_name="big_room_seconds", lookup_expr='gte',
        help_text='最少大厅总停留秒数')
    max_big_room_seconds = filters.NumberFilter(
        field_name="big_room_seconds", lookup_expr='lte',
        help_text="最大大厅总停留秒数")
    is_staff = filters.BooleanFilter(
        field_name="is_staff",
        help_text="是否为员工"
    )


    class Meta:
        model = UserInfo
        fields = (
            'min_age', 'max_age', 'name', 'gender',
            'status', 'willingness', 'self_willingness', 'net_worth',
            'is_seller', 'customerrelation__seller__user__mobile',
            'min_created', 'max_created',
            'max_spend_coin', 'min_spend_coin',
            'min_last_active_time', 'max_last_active_time',
            'min_access_times', 'max_access_times',
            'min_coin', 'max_coin', 'customerrelation__seller',
            'user__mobile', 'unbind_seller', 'min_bind_time',
            'max_bind_time', 'min_sampleroom_times', 'max_sampleroom_times',
            'min_sampleroom_seconds', 'max_sampleroom_seconds', 'min_sdver_times',
            'max_sdver_times', 'customerrelation__mark_name', 'microstore_times',
            'big_room_seconds', 'microstore_seconds', 'is_staff'
        )


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
        'willingness_list': [
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
        exclude_admin = self.request.GET.get('exclude_admin')
        if is_sampleroom == 'true':
            queryset = queryset.filter(sampleroom_times__gt=0)
        elif is_sampleroom == 'false':
            queryset = queryset.filter(sampleroom_times=0)
        if exclude_admin:
            admin = BackendUser.objects.filter(is_active=True, role__name='销售经理').values_list('mobile', flat=True)
            queryset = queryset.exclude(user__mobile__in=admin)
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

    @action(methods=['get'], url_path='list/willingness', detail=False)
    def willingness_list(self, request, *args, **kwargs):
        return Response(self.get_choice_data(UserInfo, 'willingness'))

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
        nickname = self.request.query_params.get('nickname')
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

        if nickname and not obj.name:
            obj.name = nickname
            obj.save(update_fields=['name'])

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
        help_text='备注名')
    user__user__mobile = filters.CharFilter(
        field_name="user__user__mobile", lookup_expr='icontains',
        help_text='客户手机')
    buy_done = filters.BooleanFilter(
        help_text="是否成交",
        field_name="user__buy_done",
    )

    class Meta:
        model = CustomerRelation
        fields = (
            'user__user__mobile', 'seller__user__mobile', 'mark_name', 'user__is_seller', 'user__buy_done'
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

    queryset = CustomerRelation.objects.select_related('user').order_by('created')
    serializer_class = CustomerRelationSerializer
    # filterset_fields = (
    #     'user__user__mobile',
    #     'seller__user__mobile',
    #     'mark_name',
    # )
    userfilter_field = 'seller__user__mobile'
    ordering = ('-created',)
    ordering_fields = ('user__self_willingness', 'user__access_times', 'user__last_active_time')
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


class UserCoinRecordViewSet(SellerFilterViewSet,
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

    class UserCoinRecordFilter(filters.FilterSet):
        min_created_at = filters.DateTimeFilter(
            field_name="created_at", lookup_expr='gte',
            help_text='创建时间')
        max_created_at = filters.DateTimeFilter(
            help_text='创建时间', field_name="created_at", lookup_expr='lte', )
        class Meta:
            model = PointRecord
            fields = [
                'min_created_at',
                'max_created_at',
                'user__user__mobile',
                'change_type',
                'order_no',
                'seller__mobile',
                'rule__category',
            ]

    queryset = PointRecord.objects.select_related('seller', 'user').order_by('id')
    serializer_class = PointRecordSerializer
    filterset_fields = ('rule',)
    filterset_class = UserCoinRecordFilter
    companyfilter_field = 'user__user__company_id'
    userfilter_field = 'seller__mobile'

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
    url_type = request.GET.get('type', '1')
    company_id = request.GET.get("company_id", "1")
    user = UserInfo.objects.filter(user__mobile=mobile, user__company_id=company_id).first()
    if user:
        UserBehavior.objects.create(user_id=user.user_id,
                                    category='3dvr',
                                    location='')
        user.sdver_times += 1
        user.save()
        rule = CoinRule.objects.filter(company_id=company_id, category=3).first()
        PointRecord.objects.get_or_create(
            user_id=user.user_id,
            rule=rule,
            created_at__date=date.today(),
            defaults={'coin': rule.coin, 'change_type': 'rule_reward'})

    # vr = VR.objects.filter(company_id=company_id).first()
    url = settings.VR_MAP.get(url_type, "1")
    return HttpResponseRedirect(url)



@api_view(['GET'])
@permission_classes((AllowAny, ))
def message(request):
    mobile = request.GET.get('mobile')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    company_id = request.GET.get("company_id")
    user = BaseUser.objects.filter(mobile=mobile, company_id=company_id).first()
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
        if record.change_type == "rule_reward":
            change_name = record.rule.get_category_display()
        else:
            if record.change_type == "seller_send":
                change_name = "销售赠送"
            else:
                change_name = "购物积分"
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


class DailyDataFilter(filters.FilterSet):
    min_created = filters.DateTimeFilter(
        field_name="created_at", lookup_expr='gte',
        help_text='创建日期')
    max_created = filters.DateTimeFilter(
        field_name="created_at", lookup_expr='lte',
        help_text='创建日期')
    mobile = filters.CharFilter(field_name="user__mobile",
                                help_text='手机号')


class DailyDataViewSet(CompanyFilterViewSet,
                       viewsets.GenericViewSet,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,):
    '''
    retrieve:
        获取详情
        ---

    list:
        获取列表
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = UserDailyData.objects.order_by('-created_at')
    serializer_class = UserDailyDataSerializer
    filter_class = DailyDataFilter
    companyfilter_field = 'user__company_id'


@api_view(['GET', 'POST'])
@permission_classes((AllowAny, ))
def question(request):

    mobile = request.GET.get('mobile')
    company_id = request.GET.get("company_id")

    user = BaseUser.objects.filter(company_id=company_id, mobile=mobile).first()
    if not user:
        return Response({'data': []}, status=400)

    if request.method == "GET":
        sub_titles = SubTitle.objects.filter(company_id=company_id).all()
        ret = []
        for sub_title in sub_titles:
            choice_list = sub_title.subtitlechoice_set.all()
            record = SubTitleRecord.objects.filter(user=user,
                                                   sub_title=sub_title).first()
            answers = record.choice_choose.all() if record else []
            ret.append(
                {
                    'sub_title_id': sub_title.id,
                    'sub_title_no': sub_title.no,
                    'question_content': sub_title.name,
                    'is_single': sub_title.is_single,
                    'choice_list': [{'choice_id': choice.id, 'choice_content': choice.content} for choice in
                                          choice_list],
                    'answer_list': [answer.id for answer in answers]
                }
            )

        return Response({'data': ret})
    else:
        data = json.loads(request.body.decode())
        """
        [
            {
                "sub_title_id": "",
                "answer_list": []
            }
        ]
        """
        try:
            for d in data:
                sub_title_id = d['sub_title_id']
                answer_list = d['answer_list']
                sub_title = SubTitle.objects.filter(company_id=company_id, id=sub_title_id).first()
                if sub_title.is_single and len(answer_list) > 1:
                    answer_list = answer_list[:1]
                choice_list = SubTitleChoice.objects.filter(sub_title=sub_title, id__in=answer_list).all()
                if sub_title:
                    choice = SubTitleRecord.objects.filter(
                        sub_title=sub_title, user=user).first()
                    if not choice:
                        obj = SubTitleRecord.objects.create(user=user, sub_title=sub_title)
                        obj.choice_choose.add(*choice_list)
                    else:
                        choice.choice_choose.clear()
                        choice.choice_choose.add(*choice_list)
        except Exception as e:
            return Response({'data': []}, status=400)
        return Response({'data': []})


class OSSUtils:

    @staticmethod
    def get_iso_8601(expire):
        gmt = datetime.utcfromtimestamp(expire).isoformat()
        gmt += 'Z'
        return gmt

    @staticmethod
    def get_token():
        now = int(time.time())
        expire_syncpoint = now + settings.FACE_OSS_UPLOAD_EXPIRE_TIME
        expire = OSSUtils.get_iso_8601(expire_syncpoint)
        policy_dict = {}
        policy_dict['expiration'] = expire
        condition_array = []
        array_item = []
        array_item.append('starts-with')
        array_item.append('$key')
        array_item.append(settings.FACE_OSS_UPLOAD_DIR)
        condition_array.append(array_item)
        policy_dict['conditions'] = condition_array
        policy = json.dumps(policy_dict).strip()
        policy_encode = base64.b64encode(policy.encode())
        h = hmac.new(settings.FACE_OSS_UPLOAD_ACCESS_KEY_SECRET.encode(), policy_encode, sha)
        sign_result = base64.encodestring(h.digest()).strip()
        callback_dict = {}
        callback_dict['callbackUrl'] = settings.FACE_OSS_UPLOAD_CALLBACK_URL
        callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
                                        '&height=${imageInfo.height}&width=${imageInfo.width}'
        callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'
        callback_param = json.dumps(callback_dict).strip()
        base64_callback_body = base64.b64encode(callback_param.encode())

        token_dict = {}
        token_dict['accessid'] = settings.FACE_OSS_UPLOAD_ACCESS_KEY_ID
        token_dict['host'] = settings.FACE_OSS_UPLOAD_HOST
        token_dict['policy'] = policy_encode.decode()
        token_dict['signature'] = sign_result.decode()
        token_dict['expire'] = expire_syncpoint
        token_dict['dir'] = settings.FACE_OSS_UPLOAD_DIR
        token_dict['callback'] = base64_callback_body.decode()
        return token_dict

    @staticmethod
    def get_pub_key(pub_key_url_base64):
        """ 抽取出 public key 公钥 """
        pub_key_url = base64.b64decode(pub_key_url_base64.encode())
        url_reader = urllib.request.urlopen(pub_key_url.decode())
        pub_key = url_reader.read()
        return pub_key

    @staticmethod
    def verify(auth_str, authorization_base64, pub_key):
        """
        校验签名是否正确（MD5 + RAS）
        :param auth_str: 文本信息
        :param authorization_base64: 签名信息
        :param pub_key: 公钥
        :return: 若签名验证正确返回 True 否则返回 False
        """
        pub_key_load = RSA.importKey(pub_key)
        auth_md5 = MD5.new(auth_str.encode())
        result = False
        try:
            result = PKCS1_v1_5.new(pub_key_load).verify(auth_md5, base64.b64decode(authorization_base64.encode()))
        except Exception as e:
            print(e)
            result = False
        return result

    @staticmethod
    def get_http_request_unquote(url):
        return urllib.request.unquote(url)


@api_view(['GET'])
def oss_upload(request):
    """
    :param request:
    :return:
    """
    token = OSSUtils.get_token()

    resp = JsonResponse(token)
    resp["Access-Control-Allow-Methods"] = "POST"
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


@api_view(['POST'])
@permission_classes((AllowAny, ))
def oss_upload_callback(request):
    pub_key_url = ''
    print("----------------------oss_callback_start")
    try:
        pub_key_url_base64 = request.META['HTTP_X_OSS_PUB_KEY_URL']
        pub_key = OSSUtils.get_pub_key(pub_key_url_base64)
    except Exception as e:
        print(str(e))
        print('Get pub key failed! pub_key_url : ' + pub_key_url)
        resp = HttpResponse(status=400)
        return resp

    # get authorization
    authorization_base64 = request.META['HTTP_AUTHORIZATION']

    # get callback body
    # content_length = request.META['HTTP_CONTENT_LENGTH']
    callback_body = request.body

    # compose authorization string
    pos = request.path.find('?')
    if -1 == pos:
        auth_str = request.path + '\n' + callback_body.decode()
    else:
        auth_str = OSSUtils.get_http_request_unquote(request.path[0:pos]) + request.path[pos:] + '\n' + callback_body

    result = OSSUtils.verify(auth_str, authorization_base64, pub_key)

    if not result:
        print('Authorization verify failed!')
        print('Public key : %s' % (pub_key))
        print('Auth string : %s' % (auth_str))
        resp = HttpResponse(status=400)
        return resp

    print("--------------------------------upload_success")
    try:
        query_dict = dict(urllib.parse.parse_qsl(callback_body.decode()))
        filename = query_dict['filename']
        file_url = "{}/{}".format(settings.FACE_OSS_UPLOAD_HOST_HTTPS, filename)

    except Exception as e:
        file_url = ""
        print("oss upload file callback failed")
        print(e)

    # response to OS
    resp = JsonResponse({"Status": "OK", "file_url": file_url})
    return resp

@api_view(['GET'])
def seller_replaced(request):
    current_seller_id = request.GET.get('current_seller_id')
    new_seller_id = request.GET.get('new_seller_id')

    company_id = request.user.company_id
    current_seller = BackendUser.objects.filter(pk=current_seller_id, company_id=company_id).first()
    new_seller = BackendUser.objects.filter(pk=new_seller_id, company_id=company_id).first()
    if new_seller and current_seller:
        seller = Seller.objects.get(user__mobile=new_seller.mobile, user__company_id=company_id)
        CustomerRelation.objects.filter(
            seller__user__mobile=current_seller.mobile,
        ).update(seller=seller)
    return JsonResponse({})

"""
req_body = {
    "company_id": company_id,
    "user_mobile": user_mobile,
    "change_type": change_type,
    "change_by": change_by,
    "coin": float(coin)
}
"""

@api_view(['POST'])
@permission_classes((AllowAny, ))
def bar_auth(request):
    data = json.loads(request.body.decode())
    mobile = data.get('mobile')
    password = data.get('password')
    company_id = data.get('company_id')
    user = authenticate(
        username=mobile,
        password=password,
        company_id=company_id)
    if not user:
        return JsonResponse(status=401, data={})
    user_perms = list(user.role.permissions.all().values_list('code', flat=True))
    if "product_m" not in user_perms:
        return JsonResponse(status=403, data={})
    return JsonResponse({'mobile': mobile, 'username': user.name, 'company_id': company_id})


@api_view(['GET'])
def bar_order_record(request):
    company_id = request.user.company_id
    mobile = request.GET.get('mobile')
    limit = request.GET.get('limit', 10)  # 每页最大数量
    page = request.GET.get('page', 1)  # 页码
    params = {
        "company_id": company_id,
        "mobile": mobile,
        "limit": limit,
        "page": page
    }
    res = requests.get(settings.ERP_JIAN24_URL + "/crm/bar-order-record", params=params)
    return cores(res.json())
