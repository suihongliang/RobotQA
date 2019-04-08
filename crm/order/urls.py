from django.conf.urls import url, include
from crm.order import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.OrderViewSet, 'order')
router.register(r'export', views.OrderViewSetExport, 'order_export')

urlpatterns = [
    url(r'^', include(router.urls)),
]
