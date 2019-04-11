from django.core.management.base import BaseCommand
from crm.user.models import BackendPermission


class Command(BaseCommand):
    help = 'Create Backend Permission'

    def handle(self, *args, **options):
        permissions = (
            ('customer_m', '客户管理',),
            ('product_m', '商品管理',),
            ('coin_m', '积分管理',),
            ('order_m', '订单管理',),
            ('report_m', '报表管理',),
            ('system_m', '系统管理',),
            ('system_m_read', '系统管理只读',),
            ('product_m_read', '商品管理只读',),
        )
        for code, name in permissions:
            try:
                per, created = BackendPermission.objects.get_or_create(code=code, name=name)
                if created:
                    self.stdout.write('{} created.'.format(name))
                else:
                    self.stdout.write('{} exists.'.format(name))
            except Exception:
                self.stdout.write('{} maybe exists.'.format(name))
