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
    BackendGroup,
    StayTime,
    UserVisit,
    UserDailyData,
    WebsiteConfig,
    SubTitle,
    SubTitleChoice,
    SubTitleRecord,
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
    list_display = ('id', 'mobile', 'created', 'group', 'company_id')
    list_filter = ('mobile',)


@xadmin.sites.register(BaseUser)
class BaseUserAdmin():
    '''
    '''
    list_display = ('id', 'mobile', 'company_id')
    list_filter = ('mobile',)


@xadmin.sites.register(UserInfo)
class UserInfoAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created', 'msg_last_at')
    list_filter = ('is_staff',)
    ordering = ('created',)
    list_filter = ('user__mobile',)


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
    list_display = ('user', 'mobile', 'created', 'category')
    list_filter = ('user__mobile', 'category')


@xadmin.sites.register(BackendGroup)
class BackendGroupAdmin():
    '''
    '''
    list_display = ('name', 'manager', 'created')


@xadmin.sites.register(StayTime)
class StayTimeAdmin():
    '''
    '''
    list_display = ('user', 'sample_seconds', 'micro_seconds', 'big_room_seconds', 'created_at')
    list_filter = ('user__mobile', 'created_at')


@xadmin.sites.register(UserVisit)
class UserVisitAdmin():
    '''
    '''
    list_display = (
        'all_access_total',
        'all_sample_room_total',
        'all_micro_store_total',
        'access_total',
        'register_total',
        'sample_room_total',
        'micro_store_total',
        'created_at'
    )
    list_filter = ('created_at',)


@xadmin.sites.register(UserDailyData)
class UserDailyDataAdmin():
    list_display = (
        'user',
        'created_at',
        'store_times',
        'sample_times',
        'access_times',
        'total_time',
        'store_time',
        'sample_time',
        'big_room_time'
    )


@xadmin.sites.register(WebsiteConfig)
class WebsiteConfigAdmin():
    list_display = (
        'http_host',
        'company_id',
        'config',
    )
    list_filter = ('http_host', 'company_id')


@xadmin.sites.register(SubTitle)
class SubTitleAdmin():
    list_display = (
        'no',
        'name',
        'is_single',
        'company_id',
    )
    list_filter = ('company_id',)


@xadmin.sites.register(SubTitleChoice)
class SubTitleChoiceAdmin():
    list_display = (
        'sub_title',
        'content',
    )


@xadmin.sites.register(SubTitleRecord)
class SubTitleRecordAdmin():
    list_display = (
        'user',
        'choice',
        'is_choose'
    )
