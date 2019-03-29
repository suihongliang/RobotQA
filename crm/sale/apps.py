from django.apps import AppConfig


class SaleConfig(AppConfig):
    name = 'crm.sale'

    def ready(self):
        from . import signals
