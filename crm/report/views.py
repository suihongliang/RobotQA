import math
from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import AllowAny
from datetime import datetime, date, timedelta

from rest_framework.response import Response

from crm.user.models import UserBehavior, UserInfo, UserVisit
from ..core.views import (
    custom_permission,
    )
from rest_framework.decorators import action, api_view, permission_classes
from crm.restapi.views import UserInfoViewSet, UserBehaviorViewSet, UserInfoReportViewSet, DailyDataViewSet
import urllib
from django.http import HttpResponse
from crm.report.utils import ExcelHelper, start_end
from django.views.decorators.cache import cache_page


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
            self_willingness = row['self_willingness_display']
            willingness = row['willingness_display']
            content.append([
                seller, group_name, customer_name, mobile, bind_time, last_active_time,
                model_houses, access_times, sampleroom_times, self_willingness, willingness,
                ])
        fields = ['销售', '销售团队', '用户名', '手机号', '绑定日期', '最近到访', '样板房带看',
                  '到访次数', '样板房看房次数', '主观意向度', '客观意向度']
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
            seller_group_name = row['seller']['group_name'] if row['seller'] else ''
            customer_name = row['mark_name'] if row['mark_name'] else row['name']
            mobile = row['mobile']
            self_willingness = row['self_willingness_display']
            willingness = row['willingness_display']
            gender = gender_name_dic[row['gender']]
            bind_time = str(row['bind_relation_time'] or "")
            age = row['age']
            note = row['note']
            avg_sampleroom_seconds = row['avg_sampleroom_seconds']
            avg_sampleroom_seconds = math.ceil(avg_sampleroom_seconds / 60)
            created = row['created']
            last_active_time = row['last_active_time'] or ""
            access_times = row['access_times']
            sampleroom_times = row['sampleroom_times']
            sampleroom_seconds = row['sampleroom_seconds']
            sampleroom_seconds = math.ceil(sampleroom_seconds / 60)
            microstore_times = row['microstore_times']
            microstore_seconds = row['microstore_seconds']
            microstore_seconds = math.ceil(microstore_seconds / 60)
            sdver_times = row['sdver_times']
            spend_coin = row['spend_coin']
            coupon_count = row['coupon_count']
            coin = row['coin']
            content.append([
                customer_name,
                seller_group_name,
                seller,
                mobile,
                gender,
                age,
                bind_time,
                note,
                self_willingness,
                willingness,
                avg_sampleroom_seconds,
                created,
                last_active_time,
                access_times,
                sampleroom_times,
                sampleroom_seconds,
                microstore_times,
                microstore_seconds,
                sdver_times,
                spend_coin,
                coupon_count,
                coin])
        fields = ['姓名',
                  '销售团队',
                  '专属销售人员',
                  '手机号',
                  '性别',
                  '年龄',
                  '销售绑定时间',
                  '备注',
                  '主观意向度',
                  '客观意向度',
                  '平均停留时间',
                  '用户注册日期',
                  '最近到访时间',
                  '到访次数',
                  '样板房看房次数',
                  '样板房总停留时间',
                  '小店参观次数',
                  '小店停留时间',
                  'VR看房次数',
                  '已消费积分',
                  '优惠券',
                  '积分'
                  ]
        table_name = '用户意愿报表'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(
                urllib.parse.quote_plus('用户意愿报表'))
        response.write(binary_data)
        return response


class DailyDataReport(DailyDataViewSet):
    @action(detail=False)
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = []

        for row in data:
            mobile = row['mobile']
            created_at = row['created_at']
            store_times = row['store_times']
            sample_times = row['sample_times']
            access_times = row['access_times']

            store_time = row['store_time']
            sample_time = row['sample_time']
            big_room_time = row['big_room_time']

            content.append([mobile, store_times, sample_times, access_times, store_time, sample_time, big_room_time, created_at])
        fields = ['手机号', '小店拜访次数', '样板房拜访次数', '来访次数',
                  '小店拜访时间', '样板房拜访时间', '大厅停留时间', '日期']
        table_name = '每日没人数据统计'
        with ExcelHelper(fields, content, table_name) as eh:
            binary_data = eh.to_bytes()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = \
            'attachment; filename="{0}.xls"'.format(
                urllib.parse.quote_plus('每日每人数据统计'))
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


def get_today(create_at, start, end, is_cron=False):
    """
      access: 到访(摄像头)
    signup: 注册
    sampleroom: 样板房
    sellerbind: 绑定销售
    3dvr: 3d看房
    microstore: 门店到访
    :param create_at:
    :return:
    """
    cate_set = ['access', 'sampleroom', 'microstore']
    user_id_list = UserBehavior.objects.filter(
        user__seller__isnull=True, category__in=cate_set,
        user__userinfo__is_staff=False,
        created__gte= start,
        created__lte=end,
    ).values_list('user_id', flat=True).distinct()
    all_access_total = 0
    for user_id in user_id_list:
        _count = 0
        last_at = UserBehavior.objects.filter(
            user_id=user_id,
            user__seller__isnull=True,
            created__gte=start,
            created__lte=end,
            category__in=cate_set, user__userinfo__is_staff=False).latest('created').created
        first_at = UserBehavior.objects.filter(
            user_id=user_id,
            created__gte=start,
            created__lte=end,
            user__seller__isnull=True,
            category__in=cate_set, user__userinfo__is_staff=False).latest('-created').created
        if last_at - first_at <= timedelta(hours=4):
            all_access_total += 1
            _count += 1
        elif timedelta(hours=4) < last_at - first_at <= timedelta(hours=8):
            all_access_total += 2
            _count += 2
        else:
            if UserBehavior.objects.filter(
                    created__gte=start,
                    created__lte=end,
            ).filter(
                    user_id=user_id,
                    user__seller__isnull=True, category__in=cate_set,
                    user__userinfo__is_staff=False,
                    created__gt=first_at + timedelta(hours=4),
                    created__lte=first_at + timedelta(hours=8)).exists():
                all_access_total += 3
                _count += 3
            else:
                all_access_total += 2
                _count += 2
        if is_cron:
            u = UserInfo.objects.get(user_id=user_id)
            u.access_times += _count
            u.save()

    register_total = UserInfo.objects.filter(
        is_staff = False,
        created__date=create_at).count()
    all_sample_room_total = UserBehavior.objects.filter(
        user__userinfo__is_staff = False,
        user__seller__isnull=True,
        category='sampleroom',
        location='in',
        created__gte=start,
        created__lte=end).count()
    all_micro_store_total = UserBehavior.objects.filter(
        user__userinfo__is_staff = False,
        user__seller__isnull=True,
        category='microstore',
        location='in',
        created__gte=start,
        created__lte=end).count()

    access_total = UserBehavior.objects.filter(
        user__userinfo__is_staff=False,
        user__seller__isnull=True,
        category__in=cate_set,
        created__gte=start,
        created__lte=end).values('user_id').distinct().count()

    sample_room_total = UserBehavior.objects.filter(
        user__userinfo__is_staff=False,
        user__seller__isnull=True,
        category='sampleroom',
        location='in',
        created__gte=start,
        created__lte=end).values('user_id').distinct().count()
    micro_store_total = UserBehavior.objects.filter(
        user__userinfo__is_staff=False,
        user__seller__isnull=True,
        category='microstore',
        location='in',
        created__gte=start,
        created__lte=end).values('user_id').distinct().count()
    return {
        'all_access_total': all_access_total,
        'register_total': register_total,
        'all_sample_room_total': all_sample_room_total,
        'all_micro_store_total': all_micro_store_total,
        'access_total': access_total,
        'sample_room_total': sample_room_total,
        'micro_store_total': micro_store_total,
    }


@cache_page(60)
@api_view(['GET'])
@permission_classes((AllowAny, ))
def echart_data(request):
    create_at = request.GET.get('create_at')
    if not create_at:
        create_at = timezone.now().date()
    else:
        create_at = datetime.strptime(create_at, "%Y-%m-%d").date()

    start, end = start_end(create_at)
    data = get_today(create_at, start, end)
    all_access_total = data['all_access_total']
    register_total = data['register_total']
    all_sample_room_total = data['all_sample_room_total']
    all_micro_store_total = data['all_micro_store_total']
    access_total = data['access_total']
    sample_room_total = data['sample_room_total']
    micro_store_total = data['micro_store_total']

    return cores({
        "all_access_total": all_access_total if all_access_total >= access_total else access_total,
        "all_sample_room_total": all_sample_room_total if all_sample_room_total >= sample_room_total else sample_room_total,
        "all_micro_store_total": all_micro_store_total if all_micro_store_total >= micro_store_total else micro_store_total,
        'access_total': access_total,
        'register_total': register_total,
        'sample_room_total': sample_room_total,
        'micro_store_total': micro_store_total})


@cache_page(60)
@api_view(['GET'])
@permission_classes((AllowAny, ))
def last_week_echart_data(request):
    date_range = [date.today() - timedelta(days=7-i) for i in range(1, 8)]

    data = []

    for date_at in date_range[:-1]:
        user_visit = UserVisit.objects.filter(created_at=date_at).first()
        all_access_total = user_visit.all_access_total if user_visit else 0
        all_sample_room_total = user_visit.all_sample_room_total if user_visit else 0
        all_micro_store_total = user_visit.all_micro_store_total if user_visit else 0
        access_total = user_visit.access_total if user_visit else 0
        sample_room_total = user_visit.sample_room_total if user_visit else 0
        micro_store_total = user_visit.micro_store_total if user_visit else 0
        if all_access_total > 0 and access_total == 0:
            access_total = 1
        data.append({
            "date": str(date_at)[5:],
            "register_total": user_visit.register_total if user_visit else 0,
            "access_total": access_total,
            "sample_room_total": sample_room_total,
            "micro_store_total": micro_store_total,
            "all_access_total": all_access_total if all_access_total >= access_total else access_total,
            "all_sample_room_total": all_sample_room_total if all_sample_room_total >= sample_room_total else sample_room_total,
            "all_micro_store_total": all_micro_store_total if all_micro_store_total >= micro_store_total else micro_store_total,
        })
    start, end = start_end(date_range[-1])
    ret = get_today(date_range[-1], start, end)
    all_access_total = ret['all_access_total']
    register_total = ret['register_total']
    all_sample_room_total = ret['all_sample_room_total']
    all_micro_store_total = ret['all_micro_store_total']
    access_total = ret['access_total']
    sample_room_total = ret['sample_room_total']
    micro_store_total = ret['micro_store_total']
    data.append({
        "date": str(date_range[-1])[5:],
        "register_total": register_total,
        "access_total": access_total,
        "sample_room_total": sample_room_total,
        "micro_store_total": micro_store_total,
        "all_access_total": all_access_total if all_access_total >= access_total else access_total,
        "all_sample_room_total": all_sample_room_total if all_sample_room_total >= sample_room_total else sample_room_total,
        "all_micro_store_total": all_micro_store_total if all_micro_store_total >= micro_store_total else micro_store_total,
    })
    return cores({"data": data})


@cache_page(60)
@api_view(['GET'])
@permission_classes((AllowAny, ))
def top_data(request):
    is_self = request.GET.get('is_self')
    if is_self:
        info = UserInfo.objects.exclude(status=2).filter(user__seller__isnull=True, is_staff=False).order_by('-self_willingness', '-big_room_seconds').values_list('user__mobile', 'name', 'self_willingness', 'customerrelation__mark_name')[:20]
    else:
        info = UserInfo.objects.exclude(status=2).filter(user__seller__isnull=True, is_staff=False).order_by('-willingness', '-big_room_seconds').values_list('user__mobile', 'name', 'willingness', 'customerrelation__mark_name')[:20]
    ret = [{'mobile': mobile, 'name': name, 'willingness': willingness, 'mark_name': mark_name} for mobile, name, willingness, mark_name in info]
    return cores(ret)


def cores(data):
    resp = Response(data)
    if settings.DEBUG:
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        resp[
            "Access-Control-Allow-Headers"] = "Access-Control-Allow-Methods,Origin, Accept，Content-Type, Access-Control-Allow-Origin, access-control-allow-headers,Authorization, X-Requested-With"

    return resp
