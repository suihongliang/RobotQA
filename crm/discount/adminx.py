import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    CoinRule,
    UserCoinRecord,
    Coupon,
    SendCoupon,
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
