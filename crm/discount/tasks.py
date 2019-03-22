from celery.task import Task
from .models import UserCoinRecord
import requests
from django.conf import settings


class SyncCoinTask(Task):

    def run(self, record_id):
        try:
            instance = UserCoinRecord.objects.get(id=record_id)
        except UserCoinRecord.DoseNotExists:
            return False
        # TODO: update coin
        # response = requests.get(
        #     settings.UPDATE_USER_COIN
        # )
