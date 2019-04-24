import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from crm.user.models import UserBehavior, BaseUser, UserInfo, StayTime


class Command(BaseCommand):
    help = '大厅逗留时间以及意愿度计算'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)
        user_list = UserInfo.objects.values_list('user', flat=True)
        # 当天售楼大厅停留时间(s)
        calc_big_room(user_list, today_at)

        # 计算意愿度

        for user in user_list:
            user_info = UserInfo.objects.get(user_id=user)
            a = user_info.access_times * 0.3
            b = user_info.sampleroom_times * 0.3
            c = user_info.microstore_times * 0.1
            d = user_info.sdver_times * 0.1

            e = calc_will(user_info.big_room_seconds, user_info.access_times, user_info.access_times)
            f = calc_will(user_info.sampleroom_seconds, user_info.sampleroom_times, user_info.access_times)
            g = calc_will(user_info.microstore_seconds, user_info.microstore_times, user_info.access_times)
            value = a + b + c + d + e + f + g
            print('compute-------', a, b, c, d, e, f, g)

            user_info.willingness = calc_will_flag(value)
            print('-----------------[ ', value, user_info.self_willingness)
            user_info.save()

        self.stdout.write(self.style.SUCCESS('Successfully'))


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

def calc_big_room(user_list, today_at):
    for user in user_list:
        stay, _ = StayTime.objects.get_or_create(user_id=user, created_at=today_at)

        records = list(UserBehavior.objects.filter(
            user=user,
            created__date=today_at).order_by('-created'))

        if len(records) > 1:
            end, start = records[0].created, records[-1].created
        elif len(records) == 1:
            start = end = records[0].created
        else:
            start = end = None
        print("time range", records, start, end)
        total = (end - start).seconds if start is not None else 0
        stay.big_room_seconds = total - stay.sample_seconds - stay.micro_seconds
        stay.save()
        data = StayTime.objects.filter(user_id=user).aggregate(big_room_seconds=Sum('big_room_seconds'))
        UserInfo.objects.filter(user_id=user).update(big_room_seconds=data.get('big_room_seconds', 0))
