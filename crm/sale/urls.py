from django.conf.urls import url, include
from ..sale import views
from ..sale.views import MatchFace

urlpatterns = [
    url(r'^scan_bind_seller/$', views.scan_bind_seller),
    url(r'^match_face/$', views.match_face),
    url(r'^face_match/$', MatchFace.as_view()),
]
