from django.urls import path
from crm.gaoyou.views import CustomerTendencyView, VisitMemberView, FaceMatchView, CurrentPersonView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(r'gender', CustomerTendencyView.as_view()),
    path(r'visitor', VisitMemberView.as_view()),
    path(r'current', CurrentPersonView.as_view()),
    path(r'match', csrf_exempt(FaceMatchView.as_view())),
]
