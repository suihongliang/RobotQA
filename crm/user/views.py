from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import BackendUser, WebsiteConfig
from crm.core.utils import website_config

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
        http_host = request.META["HTTP_HOST"].split(":")[0]
        try:
            company_id = WebsiteConfig.objects.get(http_host=http_host).company_id
        except WebsiteConfig.DoesNotExist:
            return JsonResponse({'detail': '域名尚未关联公司'}, status=400)
        user = authenticate(username=mobile,
                            password=password,
                            company_id=company_id)
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse(
                    {
                        'results': {
                            'mobile': mobile,
                            'company_id': user.company_id,
                            'role': user.role.name if user.role else None,
                            'username': user.username,
                        }
                    })
        else:
            if BackendUser.objects.filter(
                    username=mobile, company_id=company_id, is_active=False).exists():
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


class WebsiteConfigView(View):

    def get(self, request):
        return JsonResponse({'results': website_config(request)})


@method_decorator(csrf_exempt, name='dispatch')
class PasswordView(View):
    """修改密码"""

    def modify_password(self, username, old_password, new_password):
        user = authenticate(username=username, password=old_password)
        if user is not None:
            if user.is_active:
                user.set_password(new_password)
                user.save()
                return dict(detail='修改成功'), 200
            else:
                return dict(detail='无权限'), 403
        else:
            return dict(detail='旧密码错误'), 400

    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if username and old_password and new_password:
            result, status = self.modify_password(username, old_password, new_password)
            return JsonResponse(result, status=status)
        else:
            return JsonResponse(dict(detail='参数错误'), status=400)
