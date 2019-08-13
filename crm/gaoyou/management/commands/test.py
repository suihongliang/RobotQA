from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '每天凌晨进行插入当天的数据'

    def handle(self, *args, **options):
        print('hello world')
