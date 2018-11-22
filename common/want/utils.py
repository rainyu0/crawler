# -*- coding: utf-8 -*-


from .compat import b
import config
from base64 import urlsafe_b64encode
import hmac
import hashlib
import requests


class WantException(Exception):
    def __init__(self, message):
        self.message = message
        super(WantException, self).__init__(message)


class WantHttp():
    def __init__(self):
        self.session = requests.Session()

    def post(self, url, data, headers):
        r = self.session.post(url, data=data, headers=headers)
        body = r.json() if r.text != '' else {}
        for k in body.keys():
            if not k.islower():
                body[self._to_pep8(k)] = body.pop(k)
        body['code'] = r.status_code
        print body
        return body


    def _to_pep8(self, k):
        for i in range(len(k)):
            if k[i].isupper():
                k = (k[:i] + '_' + k[i:]).lower()
                break
        return k


def base64_urlsafe_encode(data):
    ret = urlsafe_b64encode(b(data))
    return ret

def md5(str):
    md = hashlib.md5()
    md.update(str)
    return md.hexdigest()

def hmac_sha1(key, data):
    from hashlib import sha1

    return hmac.new(key, data, sha1).hexdigest()


__all__ = [
    'WantException', 'WantHttp', 'base64_urlsafe_encode', 'hmac_sha1'
]