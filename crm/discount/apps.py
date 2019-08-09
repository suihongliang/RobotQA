from django.apps import AppConfig


class DiscountConfig(AppConfig):
    name = 'crm.discount'
    verbose_name="积分|优惠券"

    def ready(self):
        from . import signals
