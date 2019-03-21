import xadmin
# from django.http import HttpResponseRedirect
from .models import (
    Seller,
    )
# from django.utils import timezone


@xadmin.sites.register(Seller)
class SellerAdmin():
    '''
    '''
    list_display = ('user', 'mobile', 'created')
