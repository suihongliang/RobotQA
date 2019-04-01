from ..core.views import (
    custom_permission,
    )
from rest_framework.decorators import action
from crm.restapi.views import UserInfoViewSet
import urllib
from django.http import HttpResponse
from crm.report.utils import ExcelHelper


class SellerReport(UserInfoViewSet):
    """销售报表"""

    c_perms = {
        'list': [
            'report_m',
        ],
        'retrieve': [
            'report_m',
        ],
        'gender_list': [
            'report_m',
        ],
        'status_list': [
            'report_m',
        ],

    }
    permission_classes = (
        custom_permission(c_perms),
    )

    ordering = ('customerrelation__seller__name', 'created', 'gender', 'name',)

    @action(detail=False)
    def seller_report_export(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(customerrelation__seller__isnull=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            seller = row['seller']['name'] if row['seller'] else ''
            customer_name = row['name']
            mobile = row['mobile']
            bind_time = row['seller']['created'] if row['seller'] else ''
            last_active_time = row['last_active_time']
            access_times = row['access_times']
            # todo 样板房
            model_houses = ''
            willingness = row['willingness']
            net_worth = row['net_worth']
            status_display = row['status_display']
            content.append([seller, customer_name, mobile, bind_time, last_active_time,
                            model_houses, access_times, willingness, net_worth, status_display])
        fields = ['销售', '用户名', '手机号', '绑定日期', '最近到访', '样板房带看', '到访次数', '意愿度', '净值度', '状态']
        table_name = '销售报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('销售报表'))
        response.write(binary_data)
        return response


class CustomerReport(UserInfoViewSet):
    """用户信息报表"""
    c_perms = {
        'list': [
            'report_m',
        ],
        'retrieve': [
            'report_m',
        ],
        'gender_list': [
            'report_m',
        ],
        'status_list': [
            'report_m',
        ],
    }
    permission_classes = (
        custom_permission(c_perms),
    )

    @action(detail=False)
    def customer_report_export(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            customer_name = row['name']
            mobile = row['mobile']
            gender_display = row['gender_display']
            age = row['age']
            seller = row['seller']['name'] if row['seller'] else ''
            net_worth = row['net_worth']
            willingness = row['willingness']
            status_display = row['status_display']
            created = row['created']
            last_active_time = row['last_active_time']
            access_times = row['access_times']
            # todo 样板房 3D看房 优惠券
            model_houses = ''
            look_3d = ''
            coupon = ''
            coin = row['coin']
            spend_coin = row['spend_coin']
            note = row['note']
            content.append([customer_name, mobile, gender_display, age, seller, net_worth, willingness, status_display, created,
                            last_active_time, access_times, model_houses, look_3d, coupon, coin, spend_coin, note])
        fields = ['姓名', '手机号', '性别', '年龄', '销售人员', '净值度', '意愿度',
                  '状态', '注册日期', '最近来访日', '到访次数', '样板房', '3D看房', '优惠券', '积分', '已消费积分', '备注']
        table_name = '用户信息报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户信息报表'))
        response.write(binary_data)
        return response
