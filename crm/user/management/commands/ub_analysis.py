from django.core.management.base import BaseCommand, CommandError

from crm.core.utils import report_analysis_range
from crm.user.models import UserBehavior, BaseUser, UserInfo


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_at, end_at = report_analysis_range(19)

        mobile_list = UserBehavior.objects.filter(
            created__gt=start_at, created__lte=end_at).values_list(
            'user__mobile', flat=True).distinct()

        # 当天售楼大厅停留时间(s)
        calc_big_room(mobile_list, start_at, end_at)

        # 计算意愿度

        for mobile in mobile_list:
            user_info = UserInfo.objects.get(user__mobile=mobile)
            a = user_info.access_times * 0.3
            b = user_info.sampleroom_times * 0.3
            c = user_info.microstore_times * 0.1
            d = user_info.sdver_times * 0.1

            e = calc_will(user_info.big_room_seconds, user_info.access_times, user_info.access_times)
            f = calc_will(user_info.sampleroom_seconds, user_info.sampleroom_times, user_info.access_times)
            g = calc_will(user_info.microstore_seconds, user_info.microstore_times, user_info.access_times)
            value = a + b + c + d + e + f + g

            user_info.willingness = calc_will_flag(value)
            print('-----------------[ ', value, user_info.self_willingness)
            user_info.save()

        self.stdout.write(self.style.SUCCESS('Successfully'))


def calc_will(seconds, times, access_times):
    if times == 0:
        return 0
    v = (((1.0 * seconds / times if times != 0 else 0) // times) + 1) * access_times * 0.1
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

def calc_stop(mobile, ub_type, start_at, end_at):
    record_list = UserBehavior.objects.filter(
        user__mobile=mobile, category=ub_type,
        created__gt=start_at, created__lte=end_at).values_list('created', 'location').order_by('-created')
    compute_queue = []
    total_seconds = 0
    index = 0
    for at, enter_type in record_list:
        if index % 2 == 0 and enter_type == 'out':
            compute_queue.append((at, enter_type))
            index += 1
        elif index % 2 == 1 and enter_type == 'in':
            compute_queue.append((at, enter_type))
            index += 1
        else:
            continue
    if compute_queue and compute_queue[-1][1] == 'out':
        compute_queue = compute_queue[:-1]
    if compute_queue:
        start_index = 0
        for i in range(int(len(compute_queue) / 2)):
            total_seconds += (compute_queue[start_index][0] - compute_queue[start_index + 1][0]).seconds
            print("+ + +", compute_queue[start_index][0], compute_queue[start_index + 1][0])
            start_index += 2
    print("-----{}".format(total_seconds))
    return total_seconds


def calc_big_room(mobile_list, start_at, end_at):
    for mobile in mobile_list:
        records = list(UserBehavior.objects.filter(
            user__mobile=mobile,
            created__gt=start_at, created__lte=end_at).order_by('-created'))

        if len(records) > 1:
            end, start = records[0].created, records[-1].created
        elif len(records) == 1:
            start = end = records[0].created
        else:
            start = end = None
        total = (end - start).seconds if start is not None else 0
        user_info = UserInfo.objects.filter(user__mobile=mobile).first()
        if user_info:
            big_room_seconds = user_info.big_room_seconds
            sample_seconds = calc_stop(mobile, 'sampleroom', start_at, end_at)
            micro_seconds = calc_stop(mobile, 'microstore', start_at, end_at)
            user_info.big_room_seconds = big_room_seconds + total - sample_seconds - micro_seconds
            user_info.save()
            print("mobile: {} | big_room_seconds: {} | sample_seconds {} | micro_seconds: {} | total: {}".format(mobile, big_room_seconds, sample_seconds, micro_seconds, total))
