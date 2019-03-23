from django.utils.deprecation import MiddlewareMixin
import re
from django.conf import settings
import urllib
from django.http import HttpResponseForbidden
from collections import OrderedDict
import hashlib
import six
import base64
from Crypto.Cipher import AES
import logging


logger = logging.getLogger('django')


class AESCipher(object):
    def __init__(self, key):
        """
        Requires hex encoded param as a key
        """
        self.key = key

    def _pad(self, value):
        """Pad the message to be encrypted, if needed."""
        BS = 16
        P = six.b('*')
        padded = (value + (BS - len(value) % BS) * P)
        return padded

    def pkcs7padding(self, data):
        bs = AES.block_size
        padding = bs - len(data) % bs
        padding_text = six.b(chr(padding) * padding)
        return data + padding_text

    def encrypt(self, raw):
        """
        Returns hex encoded encrypted value!
        """
        value = raw.encode()
        raw = self.pkcs7padding(value)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw))


class AccessAuthMiddleware(MiddlewareMixin):
    '''
    api access
    '''

    def process_request(self, request):
        p = re.compile(r'/api/(\d\.)+\d+/.*')
        if p.match(request.path):
            signature = request.GET.get('sign')
            if not request.user.is_authenticated and signature:
                if request.method in ['GET', 'DELETE']:
                    query_string = request.META['QUERY_STRING']
                    query_dict = dict(urllib.parse.parse_qsl(query_string))
                    query_dict.pop("sign")
                    ordered_query_dict = OrderedDict(
                        sorted(query_dict.items()))
                    json_str = urllib.parse.urlencode(ordered_query_dict)
                else:
                    json_str = request.body.decode()
                try:
                    aes = AESCipher(settings.INTERNAL_KEY)
                    internal_sign = hashlib.md5(
                        aes.encrypt(
                            settings.INTERNAL_SALT + json_str)).hexdigest()
                except Exception as ex:
                    logger.exception(ex)
                    return HttpResponseForbidden('签名生成错误...')
                if internal_sign != signature:
                    return HttpResponseForbidden('签名错误...')
            elif not signature and not settings.DEBUG:
                return HttpResponseForbidden('未授权...')
