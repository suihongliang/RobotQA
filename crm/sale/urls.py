from django.conf.urls import url, include
from ..sale import views

urlpatterns = [
    url(r'^scan_bind_seller/$', views.scan_bind_seller),
]
