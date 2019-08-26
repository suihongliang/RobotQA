import requests
from datetime import datetime
from common import data_config
from common.token_utils import get_token
from django.core.management.base import BaseCommand, CommandError
from crm.gaoyou.models import EveryStatistics


class Command(BaseCommand):
    help = '每天凌晨进行插入当天的数据'

    def handle(self, *args, **options):
        data_config.headers['Authorization'] = get_token()
        str_today = datetime.today().strftime('%Y-%m-%d')
        # yesterday = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d')
        data_config.params['dateTime'] = str_today
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
            if not EveryStatistics.objects.filter(dateTime=str_today, UserType=user_type).exists():
                EveryStatistics.objects.create(
                    UserType=user_type,
                    storeId=data_config.store_id,
                    dateTime=str_today,
                    female_value=female_value,
                    male_value=male_value,
                    early_value=early_value,
                    young_value=young_value,
                    middle_value=middle_value,
                    old_value=old_value,
                )
            continue
        self.stdout.write(self.style.SUCCESS('{} Successfully {}'.format('插入成功', str_today)))
