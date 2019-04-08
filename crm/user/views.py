from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import BackendUser

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
                    {
                        'results': {
                            'mobile': mobile,
                            'company_id': user.company_id
                        }
                    })
        else:
            if BackendUser.objects.filter(
                    username=mobile, is_active=False).exists():
                return JsonResponse(
                    {'detail': '此用户被禁用'}, status=403)
        return JsonResponse(
            {'detail': '用户名或密码错误'}, status=400)


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return JsonResponse(
            {'results': {}})
