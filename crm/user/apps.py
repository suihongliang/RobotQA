from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'crm.user'
    verbose_name = "用户相关"
    def ready(self):
        from . import signals
