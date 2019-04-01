from rest_framework.response import Response
from .models import BaseUser

from django.conf import settings
import urllib
from collections import OrderedDict
import hashlib
from crm.core.middleware import AESCipher
import json

class ResInfo(Response):

    def __init__(self, msg='', data='', code=200, *arg, **kwargs):
        data = dict(code=code, msg=msg, data=data)
        super(ResInfo, self).__init__(data, *arg, **kwargs)


def get_or_create_user(mobile, company_id):
    user = BaseUser.objects.origin_all().filter(
        mobile=mobile, company_id=company_id).first()
    if not user:
        user = BaseUser.objects.create(
            mobile=mobile, company_id=company_id)
    return user


def generate_sign(query_string, method="GET"):
    aes = AESCipher(settings.INTERNAL_KEY)
    if method in ["GET", "DELETE"]:
        if not isinstance(query_string, dict):
            query_dict = dict(urllib.parse.parse_qsl(query_string))
        else:
            query_dict = query_string
        if 'sign' in query_dict:
            query_dict.pop('sign')
        ordered_query_dict = OrderedDict(sorted(query_dict.items()))
        json_str = urllib.parse.urlencode(ordered_query_dict)
    else:
        json_str = json.dumps(query_string)
    sign = hashlib.md5(aes.encrypt(settings.INTERNAL_SALT + json_str)).hexdigest()
    return sign
