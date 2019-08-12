import requests
import os
import django
from datetime import datetime, timedelta
from common import data_config
from common.token_utils import get_token
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings.settings")
django.setup()
from crm.gaoyou.models import EveryStatistics

count = 1


def insert_face_statistics():
    """
    有数据后可以设置定时任务每天获取前一天的数据，目前只获取已有的数据
    将date=datetime.today+timedelta(-),定时当天凌晨获取前一天的数据，对接后只需要获取前一天数据即可
    :return:
    """
    global count
    yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
    start_time = '2019-03-03'
    # print(today)
    data_config.headers['Authorization'] = get_token()
    # before_week = (today + timedelta(-14)).strftime('%Y-%m-%d')
    # print('上周日期:', before_week)
    # before_month = (today + timedelta(-15)).strftime('%Y-%m-%d')
    # print('上个月日期:', before_month)
    # print(before_week, before_month)

    strptime, strftime = datetime.strptime, datetime.strftime
    days = (strptime(yesterday, "%Y-%m-%d") - strptime(start_time, "%Y-%m-%d")).days  # 两个日期之间的天数
    # print(days)
    date_list = [strftime(strptime(start_time, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                 range(0, days + 1, 1)]  # 从开始到现在所有的日期
    # 对mysql中的数据进行校验判断是否已经存过，存过就不在进行存储
    for date in date_list:
        # 先判断是否存在，无责创建，有责进行下一次请求
        # b = EveryStatistics.objects.filter(dateTime=date).exists()
        # if not b:
        count += 1
        print(count)
        if count == 60:
            count = 0
            import time
            time.sleep(60)
        data_config.params['dateTime'] = date
        result = requests.get(url=data_config.face_statistics, headers=data_config.headers, params=data_config.params)
        # 获取前
        if not result.json()['data']:
            continue
        for data_info in result.json()['data']:
            print(data_info)
            user_type = data_info['userType']
            female_value = data_info['sexData'][0]['value']
            male_value = data_info['sexData'][1]['value']
            early_value = data_info['ageData'][0]['value']
            young_value = data_info['ageData'][1]['value']
            middle_value = data_info['ageData'][2]['value']
            old_value = data_info['ageData'][3]['value']
            if not EveryStatistics.objects.filter(dateTime=date, UserType=user_type).exists():
                EveryStatistics.objects.create(
                    UserType=user_type,
                    storeId=data_config.store_id,
                    dateTime=date,
                    female_value=female_value,
                    male_value=male_value,
                    early_value=early_value,
                    young_value=young_value,
                    middle_value=middle_value,
                    old_value=old_value,
                )
            continue


def get_yesterday_face_statistics():
    # 获取昨天的日期
    data_config.headers['Authorization'] = get_token()
    yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
    data_config.params['dateTime'] = yesterday
    result = requests.get(url=data_config.face_statistics, headers=data_config.headers, params=data_config.params)
    datas = result.json()['data']
    for data_info in datas:
        user_type = data_info['userType']
        female_value = data_info['sexData'][0]['value']
        male_value = data_info['sexData'][1]['value']
        early_value = data_info['ageData'][0]['value']
        young_value = data_info['ageData'][1]['value']
        middle_value = data_info['ageData'][2]['value']
        old_value = data_info['ageData'][3]['value']
        print('开始执行定时任务')
        if not EveryStatistics.objects.filter(dateTime=yesterday, UserType=user_type).exists():
            EveryStatistics.objects.create(
                UserType=user_type,
                storeId=data_config.store_id,
                dateTime=yesterday,
                female_value=female_value,
                male_value=male_value,
                early_value=early_value,
                young_value=young_value,
                middle_value=middle_value,
                old_value=old_value,
            )
        continue


sche = BlockingScheduler()
sche.add_job(get_yesterday_face_statistics, 'cron', day_of_week='0-6', hour=23, minute=59)


def run():
    insert_face_statistics()
    sche.start()


