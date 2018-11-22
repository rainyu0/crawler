#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")
import mfg_config
import httplib
import urlparse
import urllib

# db_host = 'one.xiaofudao.com'
# db_port = 3306
# db_user = 'efd_user'
# db_name = 'efd_db'
# db_passwd = 'efudao@2015'

class Http_Pool(object) :
    _client = None

    @staticmethod
    def create_client(host=mfg_config.Host, port=80) :
        Http_Pool._client = httplib.HTTPConnection(host, port, timeout=200)

    @staticmethod
    def get_client():
        return Http_Pool._client

    @staticmethod
    def close_client():
        Http_Pool._client.close()


class urlParser:
    def __init__(self, url):
        #print('get url', url)
        self.split_result =  urlparse.urlsplit(url)
        self.host = self.getHost()
        self.port = self.getPort()
        self.path = self.getPath()
        self.url_params = dict(urlparse.parse_qsl(self.split_result.query))

    def getQuery(self):
        return self.split_result.query

    def getParamsDict(self):
        return self.url_params

    def getHost(self):
        if self.split_result.netloc.find(':') != -1:
            return self.split_result.netloc.split(':')[0]
        else :
            return self.split_result.netloc

    def getPort(self):
        if self.split_result.netloc.find(':') != -1:
            return self.split_result.netloc.split(':')[1]
        else :
            return 80

    def getPath(self):
        return self.split_result.path

    def getFullUrl(self):
        url = 'http://' + self.split_result.netloc + self.path + '?'  + urllib.urlencode(self.url_params)
        return url

    def setParams(self, name, value):
        self.url_params[name] = value


if __name__ == '__main__':
    img_url = 'http://pic2.mofangge.com/upload/papers//20140823/201408230029499861099.png'
    img_parser = urlParser(img_url)
    path = img_parser.getPath()

