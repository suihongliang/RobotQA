import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from django.db.models import F

from crm.core.utils import report_analysis_range
from crm.discount.models import PointRecord
from crm.user.models import UserBehavior, BaseUser, UserInfo


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_at, end_at = report_analysis_range(19)

        mobile_list = UserBehavior.objects.filter(
            created__gt=start_at, created__lte=end_at).values_list(
            'user__mobile', flat=True).distinct()
        # for mobile in mobile_list:
        #     AnalysisReport.objects.get_or_create(
        #         created_at=datetime.date.today(), user_mobile=mobile)
        #
        # # 当天VR次数统计
        #
        # mobile_vr_map_list = UserBehavior.objects.filter(
        #     category='3dvr', created__gt=start_at, created__lte=end_at
        # ).values_list('user__mobile').annotate(vr_times=Count('category'))
        #
        # print(mobile_vr_map_list)
        # for mobile, times in mobile_vr_map_list:
        #     AnalysisReport.objects.filter(
        #         created_at=datetime.date.today(), user_mobile=mobile
        #     ).update(vr_times=times)
        #
        # # 当天消费积分
        # mobile_point_map_list = PointRecord.objects.filter(
        #     created_at__gt=start_at, created_at__lte=end_at,
        # ).values_list('user__user__mobile').annotate(spend_coin=Sum('coin')).order_by()
        # print(mobile_point_map_list)
        # for mobile, total in mobile_point_map_list:
        #     AnalysisReport.objects.filter(
        #         created_at=datetime.date.today(), user_mobile=mobile
        #     ).update(spend_coin=abs(total))
        #
        # # 当天看样板房次数
        # mobile_sample_map_list = UserBehavior.objects.filter(
        #     category='sampleroom', created__gt=start_at, created__lte=end_at
        # ).values_list('user__mobile').annotate(vr_times=Count('category'))
        # print(mobile_sample_map_list)
        # for mobile, times in mobile_sample_map_list:
        #     AnalysisReport.objects.filter(
        #         created_at=datetime.date.today(), user_mobile=mobile
        #     ).update(sample_room_times=times)
        #
        # # 当天看样板房时间(s)
        # calc_stop(mobile_list, 'sampleroom', start_at, end_at)
        #
        # # 当天小店停留时间(s)
        # calc_stop(mobile_list, 'microstore', start_at, end_at)

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

# def calc_stop(mobile_list, ub_type, start_at, end_at):
#     for mobile in mobile_list:
#         record_list = UserBehavior.objects.filter(
#             user__mobile=mobile, category=ub_type,
#             created__gt=start_at, created__lte=end_at).values_list('created', 'location').order_by('-created')
#         compute_queue = []
#         total_seconds = 0
#         index = 0
#         for at, enter_type in record_list:
#             if index % 2 == 0 and enter_type == 'out':
#                 compute_queue.append((at, enter_type))
#                 index += 1
#             elif index % 2 == 1 and enter_type == 'in':
#                 compute_queue.append((at, enter_type))
#                 index += 1
#             else:
#                 continue
#         if compute_queue and compute_queue[-1][1] == 'out':
#             compute_queue = compute_queue[:-1]
#         if compute_queue:
#             start_index = 0
#             for i in range(int(len(compute_queue) / 2)):
#                 total_seconds += (compute_queue[start_index][0] - compute_queue[start_index + 1][0]).seconds
#                 print("+ + +", compute_queue[start_index][0], compute_queue[start_index + 1][0])
#                 start_index += 2
#         print(compute_queue)
#         print("-----{}".format(total_seconds))
#         if ub_type == 'sampleroom':
#             AnalysisReport.objects.filter(
#                 created_at=datetime.date.today(), user_mobile=mobile
#             ).update(sample_room_seconds=total_seconds)
#         elif ub_type == 'microstore':
#             AnalysisReport.objects.filter(
#                 created_at=datetime.date.today(), user_mobile=mobile
#             ).update(store_seconds=total_seconds)


def calc_big_room(mobile_list, start_at, end_at):
    for mobile in mobile_list:
        records = UserBehavior.objects.filter(
            user__mobile=mobile,
            created__gt=start_at, created__lte=end_at).order_by('-created')
        if len(records) > 1:
            start, end = records[0].created, records[1].created
        elif len(records) == 1:
            start = end = records[0].created
        else:
            start = end = None
        total = (end - start).seconds if start is not None else 0
        print("big room - - - -", total)
        UserInfo.objects.filter(user__mobile=mobile).update(big_room_seconds=F('big_room_seconds')+total-F('microstore_seconds')-F('sampleroom_seconds'))
