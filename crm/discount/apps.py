from django.apps import AppConfig


class DiscountConfig(AppConfig):
    name = 'crm.discount'

    def ready(self):
        from . import signals
