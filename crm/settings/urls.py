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
from crm.report.views import echart_data, last_week_echart_data, top_data
from crm.restapi.views import sdvr, message, question, oss_upload_callback, oss_upload, seller_replaced, bar_auth
from ..restapi import views as rest_views
from ..user import views as user_views
import xadmin
from xadmin.plugins import xversion

xadmin.autodiscover()

xversion.register_models()

router = DefaultRouter()

router.register(r'user', rest_views.UserInfoViewSet)
router.register(r'user_report', rest_views.UserInfoReportViewSet)
router.register(r'useronlineorder', rest_views.UserOnlineOrderViewSet)
router.register(r'seller', rest_views.SellerViewSet)
router.register(r'coinrule', rest_views.CoinRuleViewSet)
router.register(r'usercoinrecord', rest_views.UserCoinRecordViewSet)
router.register(r'backendpermission', rest_views.BackendPermissionViewSet)
router.register(r'backendrole', rest_views.BackendRoleViewSet)
router.register(r'backenduser', rest_views.BackendUserViewSet)
router.register(r'customerrelation', rest_views.CustomerRelationViewSet)
router.register(r'coupon', rest_views.CouponViewSet)
router.register(r'sendcoupon', rest_views.SendCouponViewSet)
router.register(r'userbehavior', rest_views.UserBehaviorViewSet)
router.register(r'qrcode', rest_views.QRCodeViewSet)
router.register(r'coin_qrcode', rest_views.CoinQRCodeViewSet)
router.register(r'backendgroup', rest_views.BackendGroupViewSet)
router.register(r'daily_data', rest_views.DailyDataViewSet)

urlpatterns = [
    path(r'xadmin/', xadmin.site.urls),
    path(r'website-config/', user_views.WebsiteConfigView.as_view()),
    path(r'user/login/', user_views.LoginView.as_view()),
    path(r'user/logout/', user_views.LogoutView.as_view()),
    path(r'user/password/', user_views.PasswordView.as_view()),
    path(r'3dvr/', sdvr),
    path(r'api/1.0/', include(router.urls)),
    path(r'api/1.0/sale/', include('crm.sale.urls')),
    path(r'api/1.0/crmuser/', include('crm.user.urls')),
    path(r'api/1.0/product/', include('crm.product.urls')),
    path(r'api/1.0/order/', include('crm.order.urls')),
    path(r'api/1.0/report/', include('crm.report.urls')),
    path(r'api/1.0/message/', message),
    path(r'api/1.0/oss_upload/', oss_upload),
    path(r'api/1.0/seller-replaced/', seller_replaced),
    path(r'echart_data/', echart_data),
    path(r'last-week-echart-data/', last_week_echart_data),
    path(r'top-data/', top_data),
    path(r'question/', question),
    path(r'oss-upload-callback', oss_upload_callback),
    path(r'bar-auth/', bar_auth),
]

# if settings.DEBUG:
schema_view = get_swagger_view(title='Jian24 CRM System API')
urlpatterns += [
    path(r'docs/', schema_view),
]
