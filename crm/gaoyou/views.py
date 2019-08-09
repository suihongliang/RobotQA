import xlwt
from django.shortcuts import HttpResponse
from datetime import datetime, timedelta
from crm.gaoyou.models import EveryStatistics, FaceMatch
from crm.gaoyou.serializers import CustomerTendencyViewSerializer, FaceMatchViewSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Avg, Max, Min

today = datetime.today().strftime('%Y-%m-%d')
before_week = (datetime.today() + timedelta(-7)).strftime('%Y-%m-%d')
before_month = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')


class CustomerTendencyView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *ages, **kwargs):
        """
        客群性别、年龄比例
        :param request:
        :return:
        """
        query_sets = EveryStatistics.objects.filter(dateTime__lte=today, dateTime__gte=before_month).all()
        query_set = EveryStatistics.objects.filter(dateTime='2019-07-24').values('male_value',
                                                                                 'female_value')
        for every_data in query_set:
            customer_info = {
                'male': 0,
                'female': 0,
                'male_percent': '',
                'female_percent': '',
                'early_people': 0,
                'young_people': 0,
                'middle_people': 0,
                'old_people': 0,
                'every_customer': 0,
                'return_customer': 0,
                'early_percent': '',
                'young_percent': '',
                'middle_percent': '',
                'old_percent': '',
            }
            customer_info['every_customer'] += (every_data['male_value'] + every_data['female_value'])
        return_customer = query_set.filter(UserType=4)
        print(return_customer)
        for re_customer in return_customer:
            customer_info['return_customer'] += (re_customer['male_value'] + re_customer['female_value'])
        bs = CustomerTendencyViewSerializer(query_sets, many=True)
        for data in bs.data:
            customer_info['male'] += data['male_value']
            customer_info['female'] += data['female_value']
            customer_info['early_people'] += data['early_value']
            customer_info['young_people'] += data['young_value']
            customer_info['middle_people'] += data['middle_value']
            customer_info['old_people'] += data['old_value']
            print(data['dateTime'])
        total_customers = customer_info['male'] + customer_info['female']
        male_percent = round((customer_info['male'] / total_customers) * 100, 1)
        female_percent = round((customer_info['female'] / total_customers) * 100, 1)
        early_percent = round((customer_info['early_people'] / total_customers) * 100, 1)
        young_percent = round((customer_info['young_people'] / total_customers) * 100, 1)
        middle_percent = round((customer_info['middle_people'] / total_customers) * 100, 1)
        old_percent = round((customer_info['old_people'] / total_customers) * 100, 1)
        customer_info['male_percent'] = '%s%%' % male_percent
        customer_info['female_percent'] = '%s%%' % female_percent
        customer_info['early_percent'] = '%s%%' % early_percent
        customer_info['young_percent'] = '%s%%' % young_percent
        customer_info['middle_percent'] = '%s%%' % middle_percent
        customer_info['old_percent'] = '%s%%' % old_percent
        # print(type(Response(customer_info)))
        return Response(customer_info)


class VisitMemberView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        近7/30/90天客群趋势
        :param request:
        :return:
        """
        visit_member_tendency = {
            'seven_days': [],
            'seven_days_visitors': [],
            'thirty_days': [],
            'thirty_days_visitors': [],
            'three_months': [],
            'three_months_visitors': [],
            'current_customer': 0,
            'current_back': 0
        }

        str_today = datetime.today().strftime('%Y-%m-%d')
        # before_week = (datetime.today()+timedelta(-7)).strftime('%Y-%m-%d')
        # before_month = (datetime.today()+timedelta(-30)).strftime('%Y-%m-%d')
        # before_three_months = (datetime.today()+timedelta(-90)).strftime('%Y-%m-%d')
        week_visitor = EveryStatistics.objects.filter(dateTime__lte='2019-07-24', dateTime__gte='2019-07-17').values(
            'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))
        ont_month_visitor = EveryStatistics.objects.filter(dateTime__lte='2019-07-24',
                                                           dateTime__gte='2019-06-24').values(
            'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::3]
        three_month_visitor = EveryStatistics.objects.filter(dateTime__lte='2019-07-24',
                                                             dateTime__gte='2019-04-24').values(
            'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))[::7]
        for data in week_visitor:
            visit_member_tendency['seven_days'].append(data['dateTime'])
            visit_member_tendency['seven_days_visitors'].append(data['male'] + data['female'])

        for data in ont_month_visitor:
            visit_member_tendency['thirty_days'].append(data['dateTime'])
            visit_member_tendency['thirty_days_visitors'].append(data['male'] + data['female'])

        for data in three_month_visitor:
            visit_member_tendency['three_months'].append(data['dateTime'])
            visit_member_tendency['three_months_visitors'].append(data['male'] + data['female'])

        # 请求当天的数据，

        current_customers = EveryStatistics.objects.filter(dateTime=str_today).values(
            'dateTime').annotate(male=Sum('male_value')).annotate(female=Sum('female_value'))

        for current_customer in current_customers:
            visit_member_tendency['current_customer'] += (current_customer['male'] + current_customer['female'])
        current_back_customers = EveryStatistics.objects.filter(dateTime=str_today, UserType=4).values('dateTime',
                                                                                                       'male_value',
                                                                                                       'female_value')
        for current_back_customer in current_back_customers:
            visit_member_tendency['current_back'] += (
                    current_back_customer['male_value'] + current_back_customer['female_value'])
        # 获取当前的客流小时数
        return Response(visit_member_tendency)


class FaceMatchPagination(PageNumberPagination):
    page_size = 5  # 每页显示的多少条，可以通过前端进行传过来
    page_query_param = 'page'  # url中每页显示条数的key值
    page_size_query_param = 'size'  #
    max_page_size = 20


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
        # 通过接口获取数据存入到mysql中
        # 按时间查询后将所有字段返回给前端
        # 按人名查询后返还给前端
        # 将生成的报表导出excel格式
        # 接收前端穿过来的时间
        # 调用接口默认会按分页进行显示
        export = 1  # 用来接收前端的导出信号，接收成功则进行导出excel
        # 日期默认为空，用户不传默认为空,ajax中data是前端传过来的数据
        start_time = '2019-08-01'
        end_time = '2019-08-05'
        # 获取每页要显示的记录条数
        page_size = 10  # 从前端进行接收，接收后调用分离器组件
        from datetime import datetime
        days = (datetime.strptime(end_time, "%Y-%m-%d") - datetime.strptime(start_time, "%Y-%m-%d")).days
        print(days)
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
                            'Content-Disposition'] = 'attachment; filename=facematch.xls'  # 这里响应对象获得了附加的Content-Disposition协议头,它含有excel文件的名称,文件名随意,当浏览器访问它时,会以"另存为"对话框中使用它.
                        workbook.save(response)
                return response
            return page_obj.get_paginated_response(ser.data)  # 实现分页的功能
            # return Response(ser.data)  # 实现分页的功能

        else:
            return HttpResponse('有效结束时间不能早于开始时间')


import io
from io import BytesIO
