import datetime
from django.core.management.base import BaseCommand, CommandError

from django.db import models
from crm.user.models import UserInfo, UserVisit, UserDailyData


class Command(BaseCommand):
    help = '用户参观以及注册按天统计'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)

        ret = UserDailyData.objects.filter(created_at=today_at).values_list('created_at').annotate(
            models.Sum('store_times'),
            models.Sum('sample_times'),
            models.Sum('access_times'),
        )
        access_total = UserDailyData.objects.filter(created_at=today_at, access_times__gt=0).values(
            'user_id').distinct().count()
        sample_room_total = UserDailyData.objects.filter(created_at=today_at, sample_times__gt=0).values(
            'user_id').distinct().count()
        micro_store_total = UserDailyData.objects.filter(created_at=today_at, store_times__gt=0).values(
            'user_id').distinct().count()
        register_total = UserInfo.objects.filter(
            is_staff=False,
            created__date=today_at).count()

        created_at, store_times, sample_times, access_times = ret[0] if ret else (today_at, 0, 0, 0)
        UserVisit.objects.update_or_create(created_at=today_at, defaults={
            'all_access_total': access_times,
            'all_sample_room_total': sample_times,
            'all_micro_store_total': store_times,
            'access_total': access_total,
            'sample_room_total': sample_room_total,
            'micro_store_total': micro_store_total,
            'register_total': register_total
        })
        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(offset)))
