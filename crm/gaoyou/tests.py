from django.test import TestCase
from datetime import datetime, timedelta

# today = datetime.today()
# print(type(today))
# before_week = (today + timedelta(-15)).strftime('%Y-%m-%d')
# # print('上周日期:', before_week)
# before_month = (today + timedelta(-158)).strftime('%Y-%m-%d')
# print(before_month, before_week)
# strptime, strftime = datetime.strptime, datetime.strftime
# print(strptime, strftime)

# today = datetime.today().strftime('%Y-%m-%d')
# yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
# before_week = (datetime.today() + timedelta(-7)).strftime('%Y-%m-%d')
# before_month = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')
# before_three_month = (datetime.today() + timedelta(-90)).strftime('%Y-%m-%d')
# print(today, yesterday, before_week, before_month, before_three_month)
# strptime, strftime = datetime.strptime, datetime.strftime
# days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_month, "%Y-%m-%d")).days  # 两个日期之间的天数
# date_list = [strftime(strptime(yesterday, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
#              range(0, days + 1, 1)]  # 从开始到现在所有的日期
# print(len(date_list), date_list)
