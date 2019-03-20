from ..user.models import (
    UserInfo,
    UserOnlineOrder,
    )
from rest_framework import viewsets, mixins
from rest_framework.permissions import (
    # IsAuthenticated,
    AllowAny,
    )
from rest_framework.response import Response
# from django.http import Http404
from .serializers import (
    UserInfoSerializer,
    UserOnlineOrderSerializer,
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
        获取用户详情
        ---

    list:
        获取用户列表
        ---
    '''

    permission_classes = (
        AllowAny,
    )

    queryset = UserOnlineOrder.objects.order_by('created')
    serializer_class = UserOnlineOrderSerializer
