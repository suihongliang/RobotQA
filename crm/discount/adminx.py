import xadmin
from xadmin import views


# 创建xadmin的最基本管理器配置，并与view绑定
class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    use_bootswatch = True


# 全局修改，固定写法
class GlobalSettings(object):
    # 修改title
    site_title = 'CRM后台管理界面'
    # 修改footer
    site_footer = 'jian24的公司'
    # 收起菜单
    # menu_style = 'accordion'


# from django.http import HttpResponseRedirect
from .models import (
    CoinRule,
    Coupon,
    SendCoupon,
    CoinQRCode,
    PointRecord,
)


# from django.utils import timezone


@xadmin.sites.register(CoinRule)
class CoinRuleAdmin():
    '''
    '''
    list_display = ('get_category_display', 'created', 'coin')
    # list_filter = ['coin']
    # search_fields = ['coin']


@xadmin.sites.register(Coupon)
class CouponAdmin():
    '''
    '''
    list_display = ('id', 'description', 'discount', 'company_id', 'created')


@xadmin.sites.register(SendCoupon)
class SendCouponAdmin():
    '''
    '''
    list_display = ('id', 'backenduser', 'user', 'created')


@xadmin.sites.register(CoinQRCode)
class CoinQRCodeAdmin():
    list_display = ('code', 'coin_rule_name')

    readonly_fields = ('coin_rule_name',)

    def coin_rule_name(self, obj):
        return obj.coin_rule.get_category_display()

    coin_rule_name.short_description = '积分规则名称'


@xadmin.sites.register(PointRecord)
class PointRecordAdmin():
    list_display = ('change_type', 'user', 'coin', 'created_at', 'change_obj')
    list_filter = ('change_type',
                   'user__user__mobile',
                   'created_at',
                   'order_no',
                   'return_order_no',
                   'seller__mobile')

    readonly_fields = ('change_obj',)

    def change_obj(self, obj):
        if obj.order_no:
            return obj.order_no
        if obj.return_order_no:
            return obj.return_order_no
        if obj.seller:
            return obj.seller
        if obj.rule:
            return obj.rule
        return None

    change_obj.short_description = '变更对象'

# #
# 将基本配置管理与view绑定
xadmin.site.register(views.BaseAdminView,BaseSetting)

# 将title和footer信息进行注册
xadmin.site.register(views.CommAdminView,GlobalSettings)
