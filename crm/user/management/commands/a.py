import datetime
from django.core.management.base import BaseCommand

from crm.report.utils import start_end
from crm.user.models import UserDailyData


class Command(BaseCommand):
    help = '每日没人用户数据统计'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)
        start, end = start_end(today_at)
        UserDailyData.daily_times_compute(start, end)
        UserDailyData.daily_time_compute(start, end)

        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(offset)))
