"""dj_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
# from django.conf import settings
from ..restapi import views as rest_views
from ..user import views as user_views
import xadmin
from xadmin.plugins import xversion

xadmin.autodiscover()

xversion.register_models()

router = DefaultRouter()

router.register(r'user', rest_views.UserInfoViewSet)
router.register(r'useronlineorder', rest_views.UserOnlineOrderViewSet)
router.register(r'seller', rest_views.SellerViewSet)
router.register(r'coinrule', rest_views.CoinRuleViewSet)
router.register(r'usercoinrecord', rest_views.UserCoinRecordViewSet)
router.register(r'backendpermission', rest_views.BackendPermissionViewSet)
router.register(r'backendrole', rest_views.BackendRoleViewSet)
router.register(r'customerrelation', rest_views.CustomerRelationViewSet)

urlpatterns = [
    path(r'xadmin/', xadmin.site.urls),
    path(r'user/login', user_views.LoginView.as_view()),
    path(r'user/logout', user_views.LogoutView.as_view()),
    path(r'api/1.0/', include(router.urls)),
]

# if settings.DEBUG:
schema_view = get_swagger_view(title='Jian24 CRM System API')
urlpatterns += [
    path(r'docs/', schema_view),
]
