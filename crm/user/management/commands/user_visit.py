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
        access_total = UserBehavior.objects.filter(
            category='access',
            created__date=today_at).count()
        register_total = UserInfo.objects.filter(
            created__date=today_at).count()
        sample_room_total = UserBehavior.objects.filter(
            category='sampleroom',
            location='in',
            created__date=today_at).count()
        micro_store_total = UserBehavior.objects.filter(
            category='microstore',
            location='in',
            created__date=today_at).count()
        obj, created = UserVisit.objects.get_or_create(created_at=today_at)
        obj.access_total = access_total
        obj.register_total = register_total
        obj.sample_room_total = sample_room_total
        obj.micro_store_total = micro_store_total
        obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully {}'.format(offset)))
