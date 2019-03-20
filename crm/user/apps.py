from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'crm.user'

    def ready(self):
        from . import signals
