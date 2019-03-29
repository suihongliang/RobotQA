from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Seller, QRCode


@receiver(pre_save, sender=Seller)
def seller_save(sender, **kwargs):
    seller = kwargs['instance']
    if not seller.qrcode:
        qr_code = QRCode.objects.filter(seller__isnull=True).first()
        if qr_code:
            seller.qrcode = qr_code
