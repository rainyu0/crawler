#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import httplib
import urllib
import json
import time
import MySQLdb
import json
import re
import os
from random import Random
import random
import StringIO
import gzip

import bx_config
from common.mysql_pool import Mysql_Pool
from common.wantu_file import Wantu_File
from common.http_util import Http_Pool
from common.http_util import urlParser
from common.tree_manager import Tree_Manager
from common.log import Log

Common_Head = bx_config.getUrlHeader('bx_header')

def common_down(url_parser):
    Http_Pool.create_client(bx_config.Host)
    # params = urllib.urlencode({
    #     'type' : 3,
    #     'keypointId' : 156237,
    #     'treeId':	855,
    #     'limit'	: 5
    # })
    params = urllib.urlencode(url_parser.getParamsDict())
    #full_url = url_parser.getFullUrl()
    full_url = bx_config.Get_Question_URL
    Log.info('http request:' + full_url)
    content_length = len(params)
    #Common_Head['Content-Length'] = content_length
    Http_Pool.get_client().request("GET", full_url, params, Common_Head)
    response = Http_Pool.get_client().getresponse()
    if response.status != 200 :
        Log.error('Error Status!')
        Log.error(response.reason)
        return {}
    result_data = response.read()
    # result_data = result_data.decode("unicode_escape")
    chapter_json = json.loads(result_data, encoding="utf-8")
    Http_Pool.close_client()
    return chapter_json

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    # Wantu_File.initial()

    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    log_file = '/tmp/bx_craw_' + str(grade_id)
    Log.init_log(log_file)

    url_parser = urlParser(bx_config.Get_Question_URL)
    result_json = common_down(url_parser)
    q_list = result_json['data']['list']
    print len(q_list)
    print q_list[0]['content']
    print result_json

    Mysql_Pool.close_mysql()

