from datetime import datetime, date, timedelta

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):

    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_seize': self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'results': data
        })


def week_date_range():
    now_at = date.today()
    week_day = now_at.weekday()
    one = now_at - timedelta(days=week_day)
    next_one = now_at + timedelta(days=(6-week_day))
    return one, next_one
