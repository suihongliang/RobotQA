from django.urls import path
from crm.gaoyou.views import CustomerTendencyView, VisitMemberView, FaceMatchView

urlpatterns = [
    path(r'gender', CustomerTendencyView.as_view()),
    path(r'visitor', VisitMemberView.as_view()),
    path(r'match', FaceMatchView.as_view()),
]
