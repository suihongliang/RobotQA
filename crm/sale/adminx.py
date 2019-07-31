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
    list_display = (
        'user',
        'mobile',
        'qrcode',
        'created',
    )


@xadmin.sites.register(CustomerRelation)
class CustomerRelationAdmin():
    list_display = ('seller', 'user', 'created')


@xadmin.sites.register(QRCode)
class QRCodeAdmin():
    list_display = ('code', 'seller_mobile', 'company_id')
    readonly_fields = ('seller_mobile',)

    def seller_mobile(self, obj):
        return "{}:{}".format(obj.seller.user.company_id, obj.seller.user.mobile)

    seller_mobile.short_description = '销售'
