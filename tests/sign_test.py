from collections import OrderedDict
from Crypto.Cipher import AES
import six
import base64
import urllib
import hashlib
import requests
import json


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


INTERNAL_KEY = '8d1235sa0e212f10'
INTERNAL_SALT = 's38d'


aes = AESCipher(INTERNAL_KEY)

data = {
    'name': 'shawn',
    'age': '18',
}

# payload = OrderedDict(sorted(data.items()))
# sign = hashlib.md5(aes.encrypt(
#     INTERNAL_SALT + urllib.parse.urlencode(payload))).hexdigest()
sign = hashlib.md5(
        aes.encrypt(INTERNAL_SALT + json.dumps(data))).hexdigest()

url = 'http://127.0.0.1:8000/api/1.0/user/16608800604/?sign={}'.format(sign)
print(url)
res = requests.patch(url, json=data)
print(res.text)

payload = {
}
payload = OrderedDict(sorted(payload.items()))
sign = hashlib.md5(aes.encrypt(
    INTERNAL_SALT + urllib.parse.urlencode(payload))).hexdigest()
url = 'http://127.0.0.1:8000/api/1.0/user/16608800604/?sign={}'.format(sign)
print(url)
res = requests.get(url)
print(res.text)
