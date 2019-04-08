import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    UserBehavior,
    BackendPermission,
    BackendRole,
    BackendUser,
    )
# from django.utils import timezone


xadmin.site.unregister(BackendUser)


@xadmin.sites.register(BackendPermission)
class BackendPermissionAdmin():
    '''
    '''
    list_display = ('id', 'name', 'code')


@xadmin.sites.register(BackendRole)
class BackendRoleAdmin():
    '''
    '''
    list_display = ('id', 'name', 'created')


@xadmin.sites.register(BackendUser)
class BackendUserAdmin():
    '''
    '''
    list_display = ('id', 'mobile', 'created')


@xadmin.sites.register(BaseUser)
class BaseUserAdmin():
    '''
    '''
    list_display = ('id', 'mobile', 'company_id')


@xadmin.sites.register(UserInfo)
class UserInfoAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created', 'msg_last_at')
    ordering = ('created',)


@xadmin.sites.register(UserOnlineOrder)
class UserOnlineOrderAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created')
    ordering = ('-created',)


@xadmin.sites.register(UserBehavior)
class UserBehaviorAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created')
