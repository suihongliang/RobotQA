from rest_framework.response import Response
from .models import BaseUser


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
