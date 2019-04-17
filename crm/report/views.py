from django.utils import timezone
from rest_framework.permissions import AllowAny
from datetime import datetime, date, timedelta

from rest_framework.response import Response

from crm.user.models import UserBehavior, UserInfo
from ..core.views import (
    custom_permission,
    )
from rest_framework.decorators import action, api_view, permission_classes
from crm.restapi.views import UserInfoViewSet, UserBehaviorViewSet, UserInfoReportViewSet
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
        'willingness_list': [
            'report_m',
        ],

    }
    permission_classes = (
        custom_permission(c_perms),
    )

    ordering = ('customerrelation__seller', 'created', 'gender', 'name',)

    @action(detail=False)
    def seller(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(customerrelation__seller__isnull=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            seller = row['seller']['seller_name'] if row['seller'] else ''
            group_name = row['seller']['group_name'] if row['seller'] else ''
            customer_name = row['mark_name'] if row['mark_name'] else row['name']
            mobile = row['mobile']
            bind_time = row['bind_relation_time']
            last_active_time = row['last_active_time']
            access_times = row['access_times']
            sampleroom_times = row['sampleroom_times']
            model_houses = '已看' if row['is_sampleroom'] else '未看'
            willingness = row['willingness_display']
            content.append([
                seller, group_name, customer_name, mobile, bind_time, last_active_time,
                model_houses, access_times, sampleroom_times, willingness,
                ])
        fields = ['销售', '销售团队', '用户名', '手机号', '绑定日期', '最近到访', '样板房带看',
                  '到访次数', '样板房看房次数', '意愿度']
        table_name = '销售报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(
                urllib.parse.quote_plus('销售报表'))
        response.write(binary_data)
        return response


class UserAnalysisReport(UserInfoReportViewSet):
    """用户分析报表"""

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
        'willingness_list': [
            'report_m',
        ],

    }
    permission_classes = (
        custom_permission(c_perms),
    )

    ordering = ('created', 'gender', 'name',)

    @action(detail=False)
    def user_analysis(self, request):
        queryset = self.filter_queryset(
            self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        gender_name_dic = dict([(1, '男'), (2, '女'), (0, '未知')])
        for row in data:
            seller = row['seller']['seller_name'] if row['seller'] else ''
            customer_name = row['mark_name'] if row['mark_name'] else row['name']
            mobile = row['mobile']
            willingness = row['willingness_display']
            gender = gender_name_dic[row['gender']]
            bind_time = str(row['bind_relation_time'])
            age = row['age']
            note = row['note']
            avg_sampleroom_seconds = row['avg_sampleroom_seconds']
            created = row['created']
            last_active_time = row['last_active_time']
            access_times = row['access_times']
            sampleroom_times = row['sampleroom_times']
            sampleroom_seconds = row['sampleroom_seconds']
            microstore_times = row['microstore_times']
            microstore_seconds = row['microstore_seconds']
            big_room_seconds = row['big_room_seconds']
            sdver_times = row['sdver_times']
            spend_coin = row['spend_coin']
            coupon_count = row['coupon_count']
            coin = row['coin']
            content.append([
                customer_name,
                seller,
                mobile,
                gender,
                age,
                bind_time,
                note,
                willingness,
                avg_sampleroom_seconds,
                created,
                last_active_time,
                access_times,
                sampleroom_times,
                sampleroom_seconds,
                microstore_times,
                microstore_seconds,
                big_room_seconds,
                sdver_times,
                spend_coin,
                coupon_count,
                coin])
        # fields = ['销售', '用户名', '手机号', '绑定日期', '最近到访', '样板房带看',
        #           '到访次数', '意愿度', '净值度', '状态']
        fields = ['姓名', '专属销售人员', '手机号', '性别', '年龄', '销售绑定时间', '备注', '意向度',
                  '平均停留时间', '用户注册日期', '最近到访时间', '到访次数', '样板房看房次数',
                  '样板房总停留时间', '小店参观次数', '小店停留时间', '大厅停留时间', 'VR看房次数', '已消费积分', '优惠券', '积分']
        table_name = '用户意愿报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(
                urllib.parse.quote_plus('用户意愿报表'))
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
        'willingness_list': [
            'report_m',
        ],
    }
    permission_classes = (
        custom_permission(c_perms),
    )

    @action(detail=False)
    def customer(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            customer_name = row['mark_name'] if row['mark_name'] else row['name']
            mobile = row['mobile']
            gender_display = row['gender_display']
            age = row['age']
            seller = row['seller']['seller_name'] if row['seller'] else ''
            willingness = row['willingness_display']
            created = row['created']
            last_active_time = row['last_active_time']
            access_times = row['access_times']
            model_houses = '已看' if row['is_sampleroom'] else '未看'
            look_3d = '已看' if row['is_3dvr'] else '未看'
            coupon = row['coupon_count']
            coin = row['coin']
            spend_coin = row['spend_coin']
            note = row['note']
            content.append([
                customer_name, mobile, gender_display, age, seller,
                willingness, created, last_active_time,
                access_times, model_houses, look_3d, coupon, coin, spend_coin,
                note])
        fields = ['姓名', '手机号', '性别', '年龄', '销售人员', '意愿度',
                  '注册日期', '最近来访日', '到访次数', '样板房', '3D看房',
                  '优惠券', '积分', '已消费积分', '备注']
        table_name = '用户信息报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(
                urllib.parse.quote_plus('客户列表报表'))
        response.write(binary_data)
        return response

    @action(detail=False)
    def storespend(self, request):
        """无人店消费额"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            spend_coin = row.get('spend_coin', '')
            content.append([name, mobile, spend_coin])
        fields = ['客户名', '手机号', '小店消费']
        table_name = '小店消费报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('小店消费报表'))
        response.write(binary_data)
        return response


class UserBehaviorReport(UserBehaviorViewSet):
    """用户行为"""

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
        'willingness_list': [
            'report_m',
        ],
    }
    permission_classes = (
        custom_permission(c_perms),
    )

    @action(detail=False)
    def signup(self, request):
        """用户注册"""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category='signup', user__userinfo__is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            created = row.get('created', '')
            content.append([name, mobile, created])
        fields = ['客户名', '手机号', '注册日期']
        table_name = '用户行为注册报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户行为注册报表'))
        response.write(binary_data)
        return response

    @action(detail=False)
    def sampleroom(self, request):
        """样板房"""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category='sampleroom', user__userinfo__is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            created = row.get('created', '')
            content.append([name, mobile, created])
        fields = ['客户名', '手机号', '看样板房日期']
        table_name = '用户行为看样板房报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户行为看样板房报表'))
        response.write(binary_data)
        return response

    @action(detail=False)
    def sellerbind(self, request):
        """绑定销售"""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category='sellerbind', user__userinfo__is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            created = row.get('created', '')
            content.append([name, mobile, created])
        fields = ['客户名', '手机号', '绑定日期']
        table_name = '用户行为绑定销售报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户行为绑定销售报表'))
        response.write(binary_data)
        return response

    @action(detail=False)
    def look3d(self, request):
        """3d看房"""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category='3dvr', user__userinfo__is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            created = row.get('created', '')
            content.append([name, mobile, created])
        fields = ['客户名', '手机号', '3D看房日期']
        table_name = '用户行为3D看房报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户行为3D看房报表'))
        response.write(binary_data)
        return response

    @action(detail=False)
    def access(self, request):
        """到访记录"""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category='access', user__userinfo__is_seller=False)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []
        for row in data:
            name = row.get('name', '')
            mobile = row.get('mobile', '')
            created = row.get('created', '')
            content.append([name, mobile, created])
        fields = ['客户名', '手机号', '到访日期']
        table_name = '用户行为到访报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(urllib.parse.quote_plus('用户行为到访报表'))
        response.write(binary_data)
        return response


@api_view(['GET'])
def echart_data(request):
    create_at = request.GET.get('create_at')
    if not create_at:
        create_at = timezone.now().date()
    else:
        create_at = datetime.strptime(create_at, "%Y-%m-%d").date()
    access_total = UserBehavior.objects.filter(
        category='access',
        location='in',
        created__date=create_at).values('user_id').distinct().count()
    register_total = UserInfo.objects.filter(
        created__date=create_at).count()
    sample_room_total = UserBehavior.objects.filter(
        category='sampleroom',
        location='in',
        created__date=create_at).values('user_id').distinct().count()
    micro_store_total = UserBehavior.objects.filter(
        category='microstore',
        location='in',
        created__date=create_at).values('user_id').distinct().count()

    return Response({
        'access_total': access_total,
        'register_total': register_total,
        'sample_room_total': sample_room_total,
        'micro_store_total': micro_store_total})
