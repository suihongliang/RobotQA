from ..user.models import (
    UserInfo,
    UserOnlineOrder,
    )
from ..sale.models import (
    Seller,
    )
from rest_framework import viewsets, mixins
from rest_framework.permissions import (
    # IsAuthenticated,
    AllowAny,
    )
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.http import Http404
from .serializers import (
    UserInfoSerializer,
    UserOnlineOrderSerializer,
    SellerSerializer,
    CreateSellerSerializer,
    UpdateSellerSerializer,
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

    queryset = UserInfo.objects.order_by('created')
    serializer_class = UserInfoSerializer

    # def get_serializer_class(self):
    #     return UserInfoSerializer


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

    queryset = UserOnlineOrder.objects.order_by('created')
    serializer_class = UserOnlineOrderSerializer


class SellerViewSet(viewsets.GenericViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
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

    update_seller:
        启用禁用销售
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = Seller.objects.order_by('created')
    serializer_class = SellerSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSellerSerializer
        elif self.action == 'update_seller':
            return UpdateSellerSerializer
        return SellerSerializer

    @action(methods=['patch'], url_path='update', detail=True)
    def update_seller(self, request, *args, **kwargs):
        instance = self.get_object()
        is_seller = request.data.get('is_seller', True)
        instance.user.userinfo.is_seller = is_seller
        instance.user.userinfo.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
