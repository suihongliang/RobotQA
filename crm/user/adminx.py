import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    )
# from django.utils import timezone


@xadmin.sites.register(BaseUser)
class BaseUserAdmin():
    '''
    '''
    list_display = ('id', 'mobile', 'store_code')


@xadmin.sites.register(UserInfo)
class UserInfoAdmin():
    '''
    '''
    list_display = ('user', 'created')
    ordering = ('created',)


@xadmin.sites.register(UserOnlineOrder)
class UserOnlineOrderAdmin():
    '''
    '''
    list_display = ('user', 'created')
    ordering = ('-created',)
