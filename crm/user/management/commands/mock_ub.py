import datetime
from django.core.management.base import BaseCommand

from crm.user.models import UserBehavior, BaseUser


class Command(BaseCommand):
    help = 'mock 用户行为记录'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='天数偏移量')
        parser.add_argument('mobile', type=str, help='手机号')

    def handle(self, *args, **options):
        offset = options['offset']
        mobile = options['mobile']
        user = BaseUser.objects.get(mobile=mobile)

        now_at = datetime.datetime.now()
        y_now_at = now_at - datetime.timedelta(days=offset)
        obj = UserBehavior.objects.create(
            user=user,
            created=y_now_at,
            category="access",
            location="C0001"
        )
        obj.created = y_now_at
        obj.save()

        obj = UserBehavior.objects.create(
            user=user,
            created=y_now_at + datetime.timedelta(minutes=1),
            category="sampleroom",
            location="in"
        )
        obj.created = y_now_at + datetime.timedelta(minutes=1)
        obj.save()

        obj = UserBehavior.objects.create(
            user=user,
            created=y_now_at + datetime.timedelta(minutes=2),
            category="sampleroom",
            location="out"
        )
        obj.created = y_now_at + datetime.timedelta(minutes=2)
        obj.save()

        obj = UserBehavior.objects.create(
            user=user,
            created=y_now_at + datetime.timedelta(minutes=3),
            category="microstore",
            location="in"
        )
        obj.created = y_now_at + datetime.timedelta(minutes=3)
        obj.save()

        obj = UserBehavior.objects.create(
            user=user,
            created=y_now_at + datetime.timedelta(minutes=4),
            category="microstore",
            location="out"
        )
        obj.created = y_now_at + datetime.timedelta(minutes=4)
        obj.save()
