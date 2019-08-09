from django.apps import AppConfig


class SaleConfig(AppConfig):
    name = 'crm.sale'
    verbose_name = "销售"
    def ready(self):
        from . import signals
