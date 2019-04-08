from django.conf.urls import url, include
from crm.report import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'seller', views.SellerReport)
router.register(r'customer', views.CustomerReport)
router.register(r'userbehavior', views.UserBehaviorReport)

urlpatterns = [
    url(r'^', include(router.urls)),
]
