from rest_framework.decorators import (api_view, permission_classes, authentication_classes, )
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from crm.user.models import BaseUser, UserInfo


@api_view(['POST'])
@permission_classes((AllowAny,))
def sync_user(request):
    mobile = request.data.get('mobile')
    store_code = request.data.get('store_code', '')
    user, created = BaseUser.objects.origin_all().update_or_create(
        mobile=mobile,
        defaults={'store_code': store_code},
    )
    if created:
        result = {'msg': 'success'}

    else:
        result = {'msg': 'user exist'}
    return Response(result)



def external_info(request):
    pass