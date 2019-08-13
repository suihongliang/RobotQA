import requests
import os
import django
import pymysql
from datetime import datetime, timedelta
from common import data_config
from common.token_utils import get_token
from django.core.management.base import BaseCommand, CommandError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings.settings")
django.setup()
from crm.gaoyou.models import EveryStatistics

conn = pymysql.connect(host='localhost', user='root', password='1234', database='crm', charset='utf8')
cursor = conn.cursor()
sql = 'truncate table gaoyou_everystatistics;'
res = cursor.execute(sql)  # 执行sql语句，返回sql查询成功的记录数目,我只在表中插入一条记录，查询成功最多所以也就一条记录数
cursor.close()
conn.close()
count = 1


class Command(BaseCommand):
    help = '启动django项目时执行一次'

    # 接收参数
    # def add_arguments(self, parser):
    #     parser.add_argument('offset', type=str, help='天数转移量')

    def handle(self, *args, **options):
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
            result = requests.get(url=data_config.face_statistics, headers=data_config.headers,
                                  params=data_config.params)
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
            self.stdout.write(self.style.SUCCESS('{} Successfully {}'.format('成功', date)))
