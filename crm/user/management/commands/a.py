import datetime
from django.core.management.base import BaseCommand

from crm.report.utils import start_end
from crm.user.models import UserDailyData, BaseUser


class Command(BaseCommand):
    help = '每日没人用户数据统计'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)
        start, end = start_end(today_at)
        company_ids = BaseUser.objects.values_list('company_id', flat=True).distinct()
        for company_id in company_ids:
            UserDailyData.daily_times_compute(start, end, company_id)
            UserDailyData.daily_time_compute(start, end, company_id)

        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(offset)))
