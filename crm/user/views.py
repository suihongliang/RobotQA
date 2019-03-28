from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from crm.user.models import BaseUser, UserInfo
from crm.user.utils import ResInfo
from crm.core.views import custom_permission

logger = logging.getLogger('user_logger')


class LoginView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        '''
        登录
        '''
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        if not mobile or not password:
            return JsonResponse(
                {'detail': '密码不能空'}, status=400)
        user = authenticate(username=mobile, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse(
                    {'results': {'mobile': mobile}})
        return JsonResponse(
            {'detail': '用户名或密码错误'}, status=400)


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return JsonResponse(
            {'results': {}})


@api_view(['POST'])
@permission_classes((AllowAny,))
def sync_user(request):
    mobile = request.data.get('mobile')
    store_code = request.data.get('store_code')
    gender = request.data.get('gender')
    status = request.data.get('status')
    # logger.info('sync_user: {}'.format(request.data))
    if not store_code:
        store_code = ''
    if status == 'get':
        user, created = BaseUser.objects.origin_all().get_or_create(mobile=mobile, defaults={'store_code': store_code})
        msg = 'get'
        data = user.id
        # logger.info('sync_user: {}'.format((msg, data, created)))
    elif status == 'create':
        user, created = BaseUser.objects.origin_all().get_or_create(mobile=mobile, defaults={'store_code': store_code})
        UserInfo.objects.filter(user__mobile=mobile).update(gender=gender)
        msg = 'create'
        data = user.id
        # logger.info('sync_user: {}'.format((msg, data, created)))
    elif status == 'instore':
        user, created = BaseUser.objects.origin_all().update_or_create(
            mobile=mobile, defaults={'store_code': store_code})
        msg = 'instore'
        data = user.id
        # logger.info('sync_user: {}'.format((msg, data, created)))
    else:
        data = 0
        msg = 'not found'
    return ResInfo(msg, data)


def external_info(request):
    pass
