import datetime
from django.core.management.base import BaseCommand, CommandError

from crm.user.models import UserBehavior, BaseUser, UserInfo, StayTime, UserVisit


class Command(BaseCommand):
    help = '用户参观以及注册按天统计'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')

    def handle(self, *args, **options):
        offset = options['offset']
        today_at = datetime.date.today() - datetime.timedelta(days=offset)
        cate_set = ['access', 'sampleroom', 'microstore']

        # 到访人人次 4小时间隔 不去重 缺了用别的补
        user_id_list = UserBehavior.objects.filter(created__date=today_at, user__seller__isnull=True, category__in=cate_set).values_list('user_id', flat=True).distinct()
        all_access_total = 0
        for user_id in user_id_list:
            last_at = UserBehavior.objects.filter(user_id=user_id, created__date=today_at, user__seller__isnull=True, category__in=cate_set).latest('created').created
            first_at = UserBehavior.objects.filter(user_id=user_id, created__date=today_at, user__seller__isnull=True, category__in=cate_set).latest('-created').created

            if last_at - first_at <= datetime.timedelta(hours=4):
                all_access_total += 1
            elif datetime.timedelta(hours=4) < last_at - first_at <= datetime.timedelta(hours=8):
                all_access_total += 2
            else:
                if UserBehavior.objects.filter(
                        user_id=user_id,
                        created__date=today_at,
                        user__seller__isnull=True, category__in=cate_set,
                        created__gt=first_at+datetime.timedelta(hours=4),
                        created__lte=first_at+datetime.timedelta(hours=8)).exists():
                    all_access_total += 3
                else:
                    all_access_total += 2

        register_total = UserInfo.objects.filter(
            created__date=today_at).count()
        all_sample_room_total = UserBehavior.objects.filter(
            user__seller__isnull=True,
            category='sampleroom',
            location='in',
            created__date=today_at).count()
        all_micro_store_total = UserBehavior.objects.filter(
            user__seller__isnull=True,
            category='microstore',
            location='in',
            created__date=today_at).count()

        access_total = UserBehavior.objects.filter(
            user__seller__isnull=True,
            created__date=today_at).values('user_id').distinct().count()
        sample_room_total = UserBehavior.objects.filter(
            user__seller__isnull=True,
            category='sampleroom',
            location='in',
            created__date=today_at).values('user_id').distinct().count()
        micro_store_total = UserBehavior.objects.filter(
            user__seller__isnull=True,
            category='microstore',
            location='in',
            created__date=today_at).values('user_id').distinct().count()
        obj, created = UserVisit.objects.get_or_create(created_at=today_at)

        obj.register_total = register_total

        all_access_total = all_access_total if all_access_total >= access_total else access_total
        all_sample_room_total = all_sample_room_total if all_sample_room_total >= sample_room_total else sample_room_total
        all_micro_store_total = all_micro_store_total if all_micro_store_total >= micro_store_total else micro_store_total

        # 人次 不去重
        obj.all_sample_room_total = all_sample_room_total
        obj.all_micro_store_total = all_micro_store_total
        obj.all_access_total = all_access_total

        # 人数 去重
        obj.access_total = access_total
        obj.sample_room_total = sample_room_total
        obj.micro_store_total = micro_store_total
        obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(offset)))
