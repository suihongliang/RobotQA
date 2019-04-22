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
                            'company_id': user.company_id,
                            'role': user.role.name,
                            'username': user.username,
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


@method_decorator(csrf_exempt, name='dispatch')
class PasswordView(View):
    """修改密码"""

    def modify_password(self, username, old_password, new_password):
        user = authenticate(username=username, password=old_password)
        if user is not None:
            if user.is_active:
                user.set_password(new_password)
                user.save()
                return dict(detail='修改成功')
            else:
                return dict(detail='无权限')
        else:
            return dict(detail='用户名或密码错误')

    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if username and old_password and new_password:
            result = self.modify_password(username, old_password, new_password)
            return JsonResponse(result)
        else:
            return JsonResponse(dict(detail='参数错误'))
