from django.conf.urls import url, include
from crm.product import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.StoreProductViewSet, 'product')

urlpatterns = [
    url(r'^', include(router.urls)),
]
