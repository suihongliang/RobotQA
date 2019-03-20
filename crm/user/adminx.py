import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    BaseUser,
    UserInfo,
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
    list_display = ('user',)
    ordering = ('user',)
