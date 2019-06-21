from datetime import datetime, date, timedelta

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from crm.user.models import WebsiteConfig
import json


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


def report_analysis_range(n):
    now_at = date.today()
    today_0 = datetime(year=now_at.year, month=now_at.month, day=now_at.day)
    start_at = today_0 - timedelta(hours=24-n)
    end_at = today_0 + timedelta(hours=n)
    return start_at, end_at


def website_config(requst):
    http_host = requst.META["HTTP_HOST"].split(":")[0]
    config = {"name": "测试新城"}
    if WebsiteConfig.objects.filter(http_host=http_host).exists():
        config = json.loads(WebsiteConfig.objects.get(http_host=http_host).config)
    return config
