from django.test import TestCase
from datetime import datetime, timedelta

today = datetime.today()
print(type(today))
before_week = (today + timedelta(-15)).strftime('%Y-%m-%d')
# print('上周日期:', before_week)
before_month = (today + timedelta(-158)).strftime('%Y-%m-%d')
print(before_month, before_week)
strptime, strftime = datetime.strptime, datetime.strftime
print(strptime, strftime)
