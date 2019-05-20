import datetime
from django.core.management.base import BaseCommand, CommandError

from crm.report.utils import start_end
from crm.report.views import get_today
from crm.user.models import UserBehavior, BaseUser, UserInfo, StayTime, UserVisit


class Command(BaseCommand):
    help = '更新用户来访时间'

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
        for user_id in user_id_list:
            last_at = UserBehavior.objects.filter(
                user_id=user_id,
                user__seller__isnull=True,
                created__gte=start,
                created__lte=end).latest('created').created
            UserInfo.objects.filter(user_id=user_id).update(last_active_time=last_at)
        self.stdout.write(self.style.SUCCESS('Update Successfully {}'.format(len(user_id_list))))
