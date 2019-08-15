from django.test import TestCase

# Create your tests here.
# import qrcode
# # data = 'hello word'
# # img = qrcode.make(data=data)
# # img.show()

from datetime import datetime, timedelta

yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
before_week = (datetime.today() + timedelta(-7)).strftime('%Y-%m-%d')
before_month = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')
before_three_month = (datetime.today() + timedelta(-84)).strftime('%Y-%m-%d')
before_six_month = (datetime.today() + timedelta(-180)).strftime('%Y-%m-%d')

strptime, strftime = datetime.strptime, datetime.strftime
one_hundred_eighty_days = (strptime(yesterday, "%Y-%m-%d") - strptime(before_six_month, "%Y-%m-%d")).days  # 两个日期之间的天数
print(one_hundred_eighty_days)
one_hundred_eighty_days_list = [strftime(strptime(before_six_month, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                                range(0, one_hundred_eighty_days + 1, 1)][::-30][::-1]
print(one_hundred_eighty_days_list)
