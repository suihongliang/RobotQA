import xadmin
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
