import requests
import os
import django
# import pymysqld
from datetime import datetime, timedelta
from common import data_config
from common.token_utils import get_token
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings.settings")
django.setup()
from crm.gaoyou.models import EveryStatistics

count = 1

# conn = pymysql.connect(host='localhost', user='root', password='sui123', database='crm', charset='utf8')
# cursor = conn.cursor()
# sql = 'truncate table gaoyou_everystatistics;'
# res = cursor.execute(sql)  # 执行sql语句，返回sql查询成功的记录数目,我只在表中插入一条记录，查询成功最多所以也就一条记录数
#
#
# cursor.close()
# conn.close()


from django.db import connection

cursor = connection.cursor()
cursor.execute('truncate table gaoyou_everystatistics;')


def insert_face_statistics():
    """
    插入所有记录之前先清空表
    :return:
    """
    global count
    yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
    start_time = '2019-03-03'
    data_config.headers['Authorization'] = get_token()
    strptime, strftime = datetime.strptime, datetime.strftime
    days = (strptime(yesterday, "%Y-%m-%d") - strptime(start_time, "%Y-%m-%d")).days
    # print(days)
    date_list = [strftime(strptime(start_time, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                 range(0, days + 1, 1)]
    for date in date_list:
        count += 1
        print(count)
        if count == 60:
            count = 0
            import time
            time.sleep(60)
        data_config.params['dateTime'] = date
        result = requests.get(url=data_config.face_statistics, headers=data_config.headers, params=data_config.params)
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

#
# sche = BlockingScheduler()
# sche.add_job(get_yesterday_face_statistics, 'cron', day_of_week='0-6', hour=23, minute=59)


# def run():
#     insert_face_statistics()
#     sche.start()


insert_face_statistics()
