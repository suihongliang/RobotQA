import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    Seller,
    CustomerRelation,
    QRCode,
    )
# from django.utils import timezone


@xadmin.sites.register(Seller)
class SellerAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created')


@xadmin.sites.register(CustomerRelation)
class CustomerRelationAdmin():
    list_display = ('seller', 'user', 'created')


@xadmin.sites.register(QRCode)
class QRCodeAdmin():
    list_display = ('code', 'seller_mobile')
    readonly_fields = ('seller_mobile',)

    def seller_mobile(self, obj):
        return obj.seller.user.mobile

    seller_mobile.short_description = '销售'
