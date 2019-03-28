from django.conf.urls import url, include
from ..sale import views

urlpatterns = [
    url(r'^bind_customer/$', views.bind_customer),
]
