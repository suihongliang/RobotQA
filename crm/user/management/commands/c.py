import datetime
from django.db import models
from django.core.management.base import BaseCommand, CommandError

from crm.report.utils import start_end
from crm.user.models import UserBehavior, BaseUser, UserInfo, UserDailyData


class Command(BaseCommand):
    help = '大厅逗留时间以及意愿度计算'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)
        start, end = start_end(today_at)
        cate_set = ['access', 'sampleroom', 'microstore']
        user_id_list = UserBehavior.objects.filter(
            user__seller__isnull=True, category__in=cate_set,
            user__userinfo__is_staff=False,
            created__gte=start,
            created__lte=end,
        ).values_list('user_id', flat=True).distinct()

        ret_list = UserDailyData.objects.filter(user_id__in=user_id_list).values_list('user_id').annotate(
            models.Sum('store_times'),
            models.Sum('sample_times'),
            models.Sum('access_times'),
            models.Sum('store_time'),
            models.Sum('sample_time'),
            models.Sum('big_room_time'),
        )

        for ret in ret_list:
            uid, store_times, sample_times, access_times, store_time, sample_time, big_room_time = ret
            user_info = UserInfo.objects.get(user_id=uid)
            # 计算意愿度
            a = access_times * 0.3
            b = sample_times * 0.3
            c = store_times * 0.1
            d = user_info.sdver_times * 0.1

            e = calc_will(big_room_time, access_times, access_times)
            f = calc_will(sample_time, sample_times, sample_times)
            g = calc_will(store_time, 1 if store_times > 0 else 0, store_times)
            value = a + b + c + d + e + f + g

            user_info.microstore_times=store_times
            user_info.microstore_seconds=store_time
            user_info.sampleroom_times=sample_times
            user_info.sampleroom_seconds=sample_time
            user_info.access_times=access_times
            user_info.big_room_seconds=big_room_time
            user_info.willingness=calc_will_flag(value)
            user_info.save()

        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(len(user_id_list))))


def calc_will(seconds, times, access_times):
    if times == 0:
        return 0
    v = (((1.0 * seconds / times if times != 0 else 0) // 10) + 1) * access_times * 0.1
    return v if v < 0.9*access_times else 0.9*access_times

def calc_will_flag(v):
    if v < 1:
        return '1'
    elif 1 <= v < 2:
        return '2'
    elif 2 <= v < 3:
        return '3'
    else:
        return '4'
