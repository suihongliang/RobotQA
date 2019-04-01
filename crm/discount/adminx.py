import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    CoinRule,
    UserCoinRecord,
    Coupon,
    SendCoupon,
    CoinQRCode,
    )
# from django.utils import timezone


@xadmin.sites.register(CoinRule)
class CoinRuleAdmin():
    '''
    '''
    list_display = ('get_category_display', 'created', 'coin')


@xadmin.sites.register(UserCoinRecord)
class UserCoinRecordAdmin():
    '''
    '''
    list_display = ('mobile', 'created', 'coin', 'update_status')


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
