from django.conf.urls import url, include
from ..user import views

urlpatterns = [
    url(r'^sync_user/$', views.sync_user),
]
