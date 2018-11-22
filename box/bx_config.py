#!/usr/bin/env python
# -*- coding: utf-8 -*-

Host = 'api.knowbox.cn'
Pic_Host = 'pic2.mofangge.com'
Port = 80

Store_Path = '/home/admin/store/gfm'
Pics_Url_head = 'http://efd-p.image.alimmdn.com/'

Get_Question_URL = 'http://api.knowbox.cn/v1_tiku/course-section/question?source=androidTeacher&version=2700&channel=Knowbox&token=2vtEBmbbLtKABuWJaJVpz96x3U5flA1Wnd6%2B0nH%2B/wdf%2BgWH1erL9IypNye1q5oS&coursesection_id=172095&question_type=-1&collect=0&out=0&page_size=10&page_num=1&kbparam=9FD1B6A80DED8AA6930B570DD84CFDA3'

Know_Tree_URL = 'http://www.yuantiku.com/android/czls/users/keypoint-tree?deep=true&platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=-6501666793894305664'

# db_host = 'one.xiaofudao.com'
# db_port = 3306
# db_user = 'efd_user'
# db_name = 'efd_db'
# db_passwd = 'efudao@2015'

db_host = '10.0.0.16'
db_port = 3306
db_user = 'efd_user'
db_name = 'efd_db'
db_passwd = 'hello1234'

Min_Question_Id = 60 * 10 * 10 * 10000 * 10000000

def getUrlHeader(config_file):
    header = {}
    fileHandle = open(config_file)
    line = fileHandle.readline()
    while line:
        line = line.strip('\n')
        arr = line.split(':')
        if len(arr) != 2:
            line = fileHandle.readline()
            continue
        header[arr[0]] = arr[1]
        line = fileHandle.readline()
    return header

Url_Header = getUrlHeader('bx_header')