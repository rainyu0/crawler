#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import json
import StringIO
import gzip

from yti import yt_config
from common.mysql_pool import Mysql_Pool
from common.http_util import Http_Pool
from common.http_util import urlParser
from common.log import Log

Common_Head = yt_config.getUrlHeader('yt_header')

def common_down(url_parser, post_params=None, method='GET'):
    Http_Pool.create_client(yt_config.Host)
    params = urllib.urlencode(url_parser.getParamsDict()) if post_params is None else post_params
    full_url = url_parser.getFullUrl()
    # full_url = yt_config.Get_Question_Detail
    print ('http request:' + full_url)
    if method == 'POST':
        content_length = len(params)
        Common_Head['Content-Length'] = content_length
    Http_Pool.get_client().request(method, full_url, params, Common_Head)
    response = Http_Pool.get_client().getresponse()
    if response.status != 200 :
        Log.error('Error Status!')
        Log.error(response.reason)
        print response.reason
        print response.status
        return {}
    compresseddata = response.read()
    compressedstream = StringIO.StringIO(compresseddata)
    gzipper = gzip.GzipFile(fileobj=compressedstream)
    result_data = gzipper.read()
    # result_data = result_data.decode("unicode_escape")
    result_json = json.loads(result_data, encoding="utf-8")
    Http_Pool.close_client()
    return result_json

def get_question_ids():
    # params = urllib.urlencode({
    #     'type' : 3,
    #     'keypointId' : 156237,
    #     'treeId':	855,
    #     'limit'	: 5
    # })
    pass

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql(yt_config)
    # Wantu_File.initial()
    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    log_file = '/tmp/yt_craw_' + str(grade_id)
    Log.init_log(log_file)

    ids_params = urllib.urlencode({
        'type' : 3,
        'keypointId' : 96165,
        'treeId':	247,
        'limit'	: 10
    })
    ids_url_parser = urlParser(yt_config.Get_Paper_Ids)
    result_json = common_down(ids_url_parser, ids_params, 'POST')
    print result_json

    detail_params = {
        'ids': result_json.sheet.questionIds,
        'exerciseId': result_json.id,
        'treeId':result_json.treeId,
    }
    question_ids = result_json.sheet.questionIds



    Mysql_Pool.close_mysql()


