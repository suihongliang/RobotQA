import xlwt
import requests
from django.shortcuts import HttpResponse
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta, date
from crm.gaoyou.models import EveryStatistics, FaceMatch
from crm.gaoyou.serializers import CustomerTendencyViewSerializer, FaceMatchViewSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Avg, Max, Min
from common import data_config
from common.token_utils import get_token
from crm.user.models import UserVisit

yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
before_week = (datetime.today() + timedelta(-7)).strftime('%Y-%m-%d')
before_month = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')
before_three_month = (datetime.today() + timedelta(-84)).strftime('%Y-%m-%d')
before_six_month = (datetime.today() + timedelta(-180)).strftime('%Y-%m-%d')
strptime, strftime = datetime.strptime, datetime.strftime
# 七天
seven_days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_week, "%Y-%m-%d")).days  # 两个日期之间的天数
seven_days_list = [strftime(strptime(before_week, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                   range(0, seven_days + 1, 1)]
# print(seven_days_list)

# 三十天
thirty_days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_month, "%Y-%m-%d")).days  # 两个日期之间的天数
thirty_days_list = [strftime(strptime(before_month, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                    range(0, thirty_days + 1, 1)][::-3][::-1]
# print(len(thirty_days_list), thirty_days_list)

# 九十天
ninety_days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_three_month, "%Y-%m-%d")).days  # 两个日期之间的天数
ninety_days_list = [strftime(strptime(before_three_month, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                    range(0, ninety_days + 1, 1)][::-7][::-1]
print(len(ninety_days_list), ninety_days_list)

# 一百八十天
one_hundred_eighty_days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_six_month, "%Y-%m-%d")).days
one_hundred_eighty_days_list = [strftime(strptime(before_six_month, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for
                                i in
                                range(0, one_hundred_eighty_days + 1, 1)][::-15][::-1]


class CustomerTendencyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *ages, **kwargs):
        """
        客群性别、年龄比例
        :param request:
        :return:
        """
        customer_info = {
            'code': 200,
            'msg': 'success',
            'male': 0,
            'female': 0,
            'male_percent': '',
            'female_percent': '',
            'early_people': 0,
            'young_people': 0,
            'middle_people': 0,
            'old_people': 0,
            'early_percent': '',
            'young_percent': '',
            'middle_percent': '',
            'old_percent': '',
        }
        yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
        before_month = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')
        query_sets = EveryStatistics.objects.filter(dateTime__lte=yesterday, dateTime__gte=before_month).all()
        bs = CustomerTendencyViewSerializer(query_sets, many=True)
        # count = 0
        for data in bs.data:
            # count += 1
            # print(count)
            customer_info['male'] += data['male_value']
            customer_info['female'] += data['female_value']
            customer_info['early_people'] += data['early_value']
            customer_info['young_people'] += data['young_value']
            customer_info['middle_people'] += data['middle_value']
            customer_info['old_people'] += data['old_value']
            print(data['dateTime'])
        # print(count)
        total_customers = customer_info['male'] + customer_info['female']
        male_percent = round((customer_info['male'] / total_customers) * 100, 2)
        female_percent = round((customer_info['female'] / total_customers) * 100, 2)
        early_percent = round((customer_info['early_people'] / total_customers) * 100, 2)
        young_percent = round((customer_info['young_people'] / total_customers) * 100, 2)
        middle_percent = round((customer_info['middle_people'] / total_customers) * 100, 2)
        old_percent = round((customer_info['old_people'] / total_customers) * 100, 2)
        customer_info['male_percent'] = '%s%%' % male_percent
        customer_info['female_percent'] = '%s%%' % female_percent
        customer_info['early_percent'] = '%s%%' % early_percent
        customer_info['young_percent'] = '%s%%' % young_percent
        customer_info['middle_percent'] = '%s%%' % middle_percent
        customer_info['old_percent'] = '%s%%' % old_percent
        # print(type(Response(customer_info)))
        response = Response(customer_info)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response["Access-Control-Max-Age"] = "1000"
        response['Access-Control-Allow-Methods'] = '*'
        return response


class VisitMemberView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        近7/30/90天客群趋势
        :param request:
        :return:
        """
        visit_member_tendency = {
            'code': 200,
            'msg': 'success',
            'seven_days': [],
            'seven_days_visitors': [],
            'thirty_days': [],
            'thirty_days_visitors': [],
            'three_months': [],
            'three_months_visitors': [],
            'three_months_extrenum': [{}, {}],
            'six_month': [],
            'six_month_visitors': [],
            'six_month_extrenum': [{}, {}],

        }
        # week_visitor = EveryStatistics.objects.filter(dateTime__lte=yesterday, dateTime__gte=before_week).values(
        #     'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))
        # ont_month_visitor = EveryStatistics.objects.filter(dateTime__lte='2019-07-24',
        #                                                    dateTime__gte='2019-06-24').values(
        #     'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::3]
        # three_month_visitor = EveryStatistics.objects.filter(dateTime__lte='2019-07-24',
        #                                                      dateTime__gte='2019-04-24').values(
        #     'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::7]
        # 近七天趋势
        for day in seven_days_list:
            print(day)
            week_visitor = EveryStatistics.objects.filter(dateTime=day).values(
                'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::1]
            if len(week_visitor) == 0:
                visit_member_tendency['seven_days'].append(day)
                visit_member_tendency['seven_days_visitors'].append(0)
            else:
                print(type(week_visitor))
                visit_member_tendency['seven_days'].append(week_visitor[0]['dateTime'])
                visit_member_tendency['seven_days_visitors'].append(week_visitor[0]['male'] + week_visitor[0]['female'])
        # 近30天趋势
        for day in thirty_days_list:
            print(day)
            thirty_visitor = EveryStatistics.objects.filter(dateTime=day).values(
                'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::1]
            if len(thirty_visitor) == 0:
                visit_member_tendency['thirty_days'].append(day)
                visit_member_tendency['thirty_days_visitors'].append(0)
            else:
                print(type(thirty_visitor))
                visit_member_tendency['thirty_days'].append(thirty_visitor[0]['dateTime'])
                visit_member_tendency['thirty_days_visitors'].append(
                    thirty_visitor[0]['male'] + thirty_visitor[0]['female'])
        # 近90天趋势
        for day in ninety_days_list:
            ninety_visitor = EveryStatistics.objects.filter(dateTime=day).values(
                'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::1]
            if len(ninety_visitor) == 0:
                visit_member_tendency['three_months'].append(day)
                visit_member_tendency['three_months_visitors'].append(0)
            else:
                visit_member_tendency['three_months'].append(ninety_visitor[0]['dateTime'])
                visit_member_tendency['three_months_visitors'].append(
                    ninety_visitor[0]['male'] + ninety_visitor[0]['female'])
        min_value = min(visit_member_tendency['three_months_visitors'])
        min_date = visit_member_tendency['three_months'][
            visit_member_tendency['three_months_visitors'].index(min_value)]
        max_value = max(visit_member_tendency['three_months_visitors'])
        max_date = visit_member_tendency['three_months'][
            visit_member_tendency['three_months_visitors'].index(max_value)]
        visit_member_tendency['three_months_extrenum'][0]['min_date'] = min_date
        visit_member_tendency['three_months_extrenum'][0]['min_value'] = min_value
        visit_member_tendency['three_months_extrenum'][1]['max_date'] = max_date
        visit_member_tendency['three_months_extrenum'][1]['max_value'] = max_value
        # 近半年的趋势
        for day in one_hundred_eighty_days_list:
            ninety_visitor = EveryStatistics.objects.filter(dateTime=day).values(
                'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::1]
            if len(ninety_visitor) == 0:
                visit_member_tendency['six_month'].append(day)
                visit_member_tendency['six_month_visitors'].append(0)
            else:
                visit_member_tendency['six_month'].append(ninety_visitor[0]['dateTime'])
                visit_member_tendency['six_month_visitors'].append(
                    ninety_visitor[0]['male'] + ninety_visitor[0]['female'])
        min_value = min(visit_member_tendency['six_month_visitors'])
        min_date = visit_member_tendency['six_month'][visit_member_tendency['six_month_visitors'].index(min_value)]
        max_value = max(visit_member_tendency['six_month_visitors'])
        max_date = visit_member_tendency['six_month'][visit_member_tendency['six_month_visitors'].index(max_value)]
        visit_member_tendency['six_month_extrenum'][0]['min_date'] = min_date
        visit_member_tendency['six_month_extrenum'][0]['min_value'] = min_value
        visit_member_tendency['six_month_extrenum'][1]['max_date'] = max_date
        visit_member_tendency['six_month_extrenum'][1]['max_value'] = max_value
        # 近7天趋势
        # for data in week_visitor:
        #     visit_member_tendency['seven_days'].append(data['dateTime'])
        #     visit_member_tendency['seven_days_visitors'].append(data['male'] + data['female'])
        # 近一个月趋势
        # for data in ont_month_visitor:
        #     visit_member_tendency['thirty_days'].append(data['dateTime'])
        #     visit_member_tendency['thirty_days_visitors'].append(data['male'] + data['female'])
        # 近三个月趋势
        # for data in three_month_visitor:
        #     visit_member_tendency['three_months'].append(data['dateTime'])
        #     visit_member_tendency['three_months_visitors'].append(data['male'] + data['female'])
        response = Response(visit_member_tendency)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response["Access-Control-Max-Age"] = "1000"
        response['Access-Control-Allow-Methods'] = '*'
        return response


class CurrentPersonView(APIView):
    # 前端每一个小时对该接口记性请求一次获取最新数据
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        当天客流量和回头客
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        current_people = {
            'code': 200,
            'msg': 'success',
            'current_customer': 0,
            'current_back': 0
        }
        str_today = datetime.today().strftime('%Y-%m-%d')
        data_config.headers['Authorization'] = get_token()
        data_config.params['dateTime'] = str_today
        result = requests.get(url=data_config.face_statistics, headers=data_config.headers, params=data_config.params)
        for current_data in result.json()['data']:
            current_people['current_customer'] += current_data['totalNum']
            if current_data['userType'] == 4:
                current_people['current_back'] = current_data['totalNum']
        response = Response(current_people)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response["Access-Control-Max-Age"] = "1000"
        response['Access-Control-Allow-Methods'] = '*'
        return response


class FaceMatchPagination(PageNumberPagination):
    # page_size = 5  # 每页显示的多少条，可以通过前端进行传过来
    # page_query_param = 'page'  # url中每页显示条数的key值
    # page_size_query_param = 'size'  #
    # max_page_size = 20

    page_query_description = '页面查询描述'
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),  # 下一页
            'previous': self.get_previous_link(),  # 上一页
            'page': self.page.number,  # 当前页码
            'page_seize': self.get_page_size(self.request),  # 每页显示的记录条数，默认显示15条
            'count': self.page.paginator.count,  # 总共查询出来的记录条数
            'results': data  # 每条记录的详细内容
        })


# 进行人脸匹配
class FaceMatchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        人脸匹配，按时间和进行搜索并能将报表进行导出
        :param request:
        :return:
        """
        # 人脸匹配
        # start_time = request.GET.get('start')
        # end_time = request.GET.get('end')    # 进行筛选
        # export = request.GET.get('export)  # 获取导出的信号做判断，默认是0，触发是变为1
        export = 1  # 用来接收前端的导出信号，接收成功则进行导出excel
        start_time = '2019-01-01'
        end_time = '2019-12-05'
        # page_size = 10  # 从前端进行接收，接收后调用分离器组件
        # 将上一页下一页的生成的url传过去，没有对应的就是null，ajax获取后端传过来的数据
        days = (datetime.strptime(end_time, "%Y-%m-%d") - datetime.strptime(start_time, "%Y-%m-%d")).days
        if request.is_ajax():
            array = request.POST.getlist('ids')
        if days >= 0:
            query_set = FaceMatch.objects.filter(time__gte=start_time, time__lte=end_time)
            query_set_list = FaceMatch.objects.filter(time__gte=start_time, time__lte=end_time).values_list('username',
                                                                                                            'phone',
                                                                                                            'time',
                                                                                                            'library_picture',
                                                                                                            'grap_picture',
                                                                                                            'result')
            page_obj = FaceMatchPagination()
            page_res = page_obj.paginate_queryset(queryset=query_set, request=request, view=self)
            ser = FaceMatchViewSerializer(instance=page_res, many=True)
            if export == 2:
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=facematch.xls'  # 返回下载文件的名称(activity.xls)
                workbook = xlwt.Workbook(encoding='utf-8')  # 创建工作簿
                mysheet = workbook.add_sheet(u'Sheet1')  # 创建工作页
                rows = query_set_list
                cols = 6
                table_header = ['用户名', '手机号', '匹配时间 ', '脸库图片', '捕获图片', '分页结果']  # 表头名
                for c in range(len(table_header)):
                    mysheet.write(0, c, table_header[c])  # 头信息
                for r in range(0, len(rows)):  # 对行进行遍历
                    for c in range(cols):  # 对列进行遍历
                        mysheet.write(r + 1, c, str(rows[r][c]))  # 每行信息
                        response = HttpResponse(
                            content_type='application/vnd.ms-excel')  # 这里响应对象获得了一个特殊的mime类型,告诉浏览器这是个excel文件不是html
                        response[
                            'Content-Disposition'] = 'attachment; filename=facematch.xls'
                        # 这里响应对象获得了附加的Content-Disposition协议头,它含有excel文件的名称,文件名随意,当浏览器访问它时,会以"另存为"对话框中使用它.
                        workbook.save(response)
                return response
            return page_obj.get_paginated_response(ser.data)  # 实现分页的功能
            # return Response(ser.data)  # 实现分页的功能
        else:
            return HttpResponse('有效结束时间不能早于开始时间')


class MemberTendency(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        会员到访数据走势
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        visit_member_tendency = {
            'code': 200,
            'msg': 'success',
            'seven_days': [],
            'seven_days_visitors': [],
            'thirty_days': [],
            'thirty_days_visitors': [],
            'three_months': [],
            'three_months_visitors': [],
            'three_months_extrenum': [{}, {}],
            'six_months': [],
            'six_month_visitors': [],
            'six_month_extrenum': [{}, {}],

        }
        seven_date_range = [(date.today() - timedelta(days=7 - i)).strftime('%Y-%m-%d') for i in range(0, 7)]
        thirty_date_range = [(date.today() - timedelta(days=30 - i)).strftime('%Y-%m-%d') for i in range(1, 30)][::-3][
                            ::-1]
        three_months_range = [(date.today() - timedelta(days=90 - i)).strftime('%Y-%m-%d') for i in range(7, 90)][::-7][
                             ::-1]
        six_months_range = [(date.today() - timedelta(days=180 - i)).strftime('%Y-%m-%d') for i in range(1, 180)][
                           ::-15][::-1]
        # print(seven_date_range)
        # print(thirty_date_range)
        # print(three_months_range)
        # print(six_months_range)
        for date_at in seven_date_range:
            user_visit = UserVisit.objects.filter(created_at=date_at, company_id='4').values('access_total')
            if not user_visit:
                visit_member_tendency['seven_days_visitors'].append(0)
            for access_total in user_visit:
                print(date_at, access_total)
                visit_member_tendency['seven_days'] = seven_date_range
                visit_member_tendency['seven_days_visitors'].append(access_total['access_total'])

        print(visit_member_tendency['seven_days_visitors'])

        for date_at in thirty_date_range:
            user_visit = UserVisit.objects.filter(created_at=date_at, company_id='4').values('access_total')
            if not user_visit:
                visit_member_tendency['thirty_days_visitors'].append(0)
            else:
                for access_total in user_visit:
                    print(date_at, access_total)
                    visit_member_tendency['thirty_days'] = thirty_date_range
                    visit_member_tendency['thirty_days_visitors'].append(access_total['access_total'])

        for date_at in three_months_range:
            user_visit = UserVisit.objects.filter(created_at=date_at, company_id='4').values('access_total')
            if not user_visit:
                visit_member_tendency['three_months_visitors'].append(0)
            else:
                for access_total in user_visit:
                    print(date_at, access_total)
                    visit_member_tendency['three_months'] = three_months_range
                    visit_member_tendency['three_months_visitors'].append(access_total['access_total'])
        min_value = min(visit_member_tendency['three_months_visitors'])
        min_date = visit_member_tendency['three_months'][
            visit_member_tendency['three_months_visitors'].index(min_value)]
        max_value = max(visit_member_tendency['three_months_visitors'])
        max_date = visit_member_tendency['three_months'][
            visit_member_tendency['three_months_visitors'].index(max_value)]
        visit_member_tendency['three_months_extrenum'][0]['min_date'] = min_date
        visit_member_tendency['three_months_extrenum'][0]['min_value'] = min_value
        visit_member_tendency['three_months_extrenum'][1]['max_date'] = max_date
        visit_member_tendency['three_months_extrenum'][1]['max_value'] = max_value

        for date_at in six_months_range:
            user_visit = UserVisit.objects.filter(created_at=date_at, company_id='4').values('access_total')
            if not user_visit:
                visit_member_tendency['six_month_visitors'].append(0)
            else:
                for access_total in user_visit:
                    print(date_at, access_total)
                    visit_member_tendency['six_months'] = six_months_range
                    visit_member_tendency['six_month_visitors'].append(access_total['access_total'])
        min_value = min(visit_member_tendency['six_month_visitors'])
        min_date = visit_member_tendency['six_months'][visit_member_tendency['six_month_visitors'].index(min_value)]
        max_value = max(visit_member_tendency['six_month_visitors'])
        max_date = visit_member_tendency['six_months'][visit_member_tendency['six_month_visitors'].index(max_value)]
        visit_member_tendency['six_month_extrenum'][0]['min_date'] = min_date
        visit_member_tendency['six_month_extrenum'][0]['min_value'] = min_value
        visit_member_tendency['six_month_extrenum'][1]['max_date'] = max_date
        visit_member_tendency['six_month_extrenum'][1]['max_value'] = max_value
        response = Response(visit_member_tendency)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response["Access-Control-Max-Age"] = "1000"
        response['Access-Control-Allow-Methods'] = '*'
        return response
