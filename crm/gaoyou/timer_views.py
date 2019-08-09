import requests
import os
import django
from datetime import datetime, timedelta
from common import data_config
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings.settings")
django.setup()
from crm.gaoyou.models import EveryStatistics

data = {
    'grant_type': 'client_credentials',
    'scope': 'app',
    'client_id': '9fb3d5bdb511474b9637a71745a08538',
    'client_secret': '8fbe7dcfd5084290ad6f19ccb670e7ec'
}

headers = {
    'Host': 'api2.hik-cloud.com',
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
}

url = 'https://api2.hik-cloud.com/oauth/token'
params = {}
store_id = 'e99d034135664536badbd93f778cfdb1'
params['storeId'] = store_id


def get_token():
    result = requests.post(url=url, headers=headers, data=data)
    access_token = result.json()['access_token']
    token_type = result.json()['token_type']
    authorization = token_type + " " + access_token
    return authorization


count = 1


def insert_face_statistics():
    """
    有数据后可以设置定时任务每天获取前一天的数据，目前只获取已有的数据
    将date=datetime.today+timedelta(-),定时当天凌晨获取前一天的数据，对接后只需要获取前一天数据即可
    :return:
    """
    global count
    str_today = datetime.today().strftime('%Y-%m-%d')
    start_time = '2019-03-03'
    # print(today)
    headers['Authorization'] = get_token()
    # before_week = (today + timedelta(-14)).strftime('%Y-%m-%d')
    # print('上周日期:', before_week)
    # before_month = (today + timedelta(-15)).strftime('%Y-%m-%d')
    # print('上个月日期:', before_month)
    # print(before_week, before_month)

    strptime, strftime = datetime.strptime, datetime.strftime
    days = (strptime(str_today, "%Y-%m-%d") - strptime(start_time, "%Y-%m-%d")).days  # 两个日期之间的天数
    # print(days)
    date_list = [strftime(strptime(start_time, "%Y-%m-%d") + timedelta(i), "%Y-%m-%d") for i in
                 range(0, days + 1, 1)]  # 从开始到现在所有的日期
    for date in date_list:
        # 先判断是否存在，无责创建，有责进行下一次请求
        # b = EveryStatistics.objects.filter(dateTime=date).exists()
        # if not b:
        count += 1
        if count == 60:
            count = 0
            import time
            time.sleep(60)
        params['dateTime'] = date
        result = requests.get(url=data_config.face_statistics, headers=headers, params=params)
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
                    storeId=store_id,
                    dateTime=date,
                    female_value=female_value,
                    male_value=male_value,
                    early_value=early_value,
                    young_value=young_value,
                    middle_value=middle_value,
                    old_value=old_value,
                )
            continue

    params['dateTime'] = str_today

    # 获取当天的数据存入到mysql中，将当天的数据抽取出来进行更新
    result = requests.get(url=data_config.face_statistics, headers=headers, params=params)
            # 获取当天的数据将数据存入到mysql中，有则更新无责创建
        # 创建文件
        # params['dateTime'] = date
        # result = requests.get(url=data_config.face_statistics, headers=headers, params=params)
        # for data_info in result.json()['data']:
        #     user_type = data_info['userType']
        #     female_value = data_info['sexData'][0]['value']
        #     male_value = data_info['sexData'][1]['value']
        #     early_value = data_info['ageData'][0]['value']
        #     young_value = data_info['ageData'][1]['value']
        #     middle_value = data_info['ageData'][2]['value']
        #     old_value = data_info['ageData'][3]['value']
        #     EveryStatistics.objects.update_or_create(defaults={'UserType': user_type, 'dateTime': date},
        #                                              UserType=user_type,
        #                                              storeId=store_id,
        #                                              dateTime=date,
        #                                              female_value=female_value,
        #                                              male_value=male_value,
        #                                              early_value=early_value,
        #                                              young_value=young_value,
        #                                              middle_value=middle_value,
        #                                              old_value=old_value,
        #                                              )

    # count = 1
    # for date in date_list:
    #     params["dateTime"] = date  # 将日期换成今天的日期
    #     print(params)
    #     count += 1
    #     if count == 90:
    #         import time
    #         time.sleep(60)
    #     result = requests.get(url=data_config.face_statistics, headers=headers, params=params)
    #     if result.json()['data']:
    #         continue
    #     print(result, '\n', headers, '\n', params)
    #     for data in result.json()['data']:
    #         user_type = data['userType']
    #         female_value = data['sexData'][0]['value']
    #         male_value = data['sexData'][1]['value']
    #         early_value = data['ageData'][0]['value']
    #         young_value = data['ageData'][1]['value']
    #         middle_value = data['ageData'][2]['value']
    #         old_value = data['ageData'][3]['value']
    #         if EveryStatistics.objects.filter(UserType=user_type, dateTime=date).exists():
    #             continue
    # EveryStatistics.objects.create(
    #     UserType=user_type,
    #     storeId=store_id,
    #     dateTime=date,
    #     female_value=female_value,
    #     male_value=male_value,
    #     early_value=early_value,
    #     young_value=young_value,
    #     middle_value=middle_value,
    #     old_value=old_value,
    # )


insert_face_statistics()
# sche = BlockingScheduler()
# 每日凌晨进行更新前一天的数据
# sche.add_job(insert_face_statistics, 'corn', day_of_week='0-6', hour=0, minute=0)
