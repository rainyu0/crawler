#!/usr/bin/env python
# -*- coding: utf-8 -*-

Host = 'www.yuantiku.com'
Pic_Host = 'gallery.fbcontent.cn'
Pic_Url = '/android/tarzan/images/IMAGE?width=0&height=200&strict=false&version=1.0.0'
Png_Pic_Url = '/android/tarzan/images/IMAGE?width=1092&height=0'
SVG_Pic_Url = '/android/tarzan/svgs/batch?imageIds=IMAGE'

Tex_Host = '10.0.0.104'
Tex_Url = '/index?get=IMAGE'
Tex_Port = 8080

Port = 80

Store_Path = '/home/admin/store/yt'
Pics_Url_head = 'http://efd-p.image.alimmdn.com/'

Get_Question_Detail = 'http://www.yuantiku.com/android/czsx/questions/bundle?exerciseId=625435459&treeId=297&ids=1219537,1355039,1384807&platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=7711888079992669590&sign=b1d974fe5eabb5b25a4ce2ea90b12095'

Get_Paper_Ids = 'http://www.yuantiku.com/android/czdl/exercises?platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=7711888079992669590'

Books_Tree_Url = 'http://www.yuantiku.com/android/czls/users/keypoint-tree?deep=true&platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=-6501666793894305664'

Version_Url = 'http://www.yuantiku.com/android/COURSE/keypoint-trees?platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=7711888079992669590'
Know_Url = 'http://www.yuantiku.com/android/COURSE/users/keypoint-tree?deep=true&treeId=TREEID&platform=android22&version=5.5.0&vendor=tencent&av=11&_productId=111&_deviceId=7711888079992669590'

compare_check = {
    'subject' : {'yw' : 2, 'sx' : 1, 'yy' : 3, 'wl' : 7, 'hx': 8, 'sw':9, 'ls':5, 'dl': 6, 'kx': 14,
                 'lh':18, 'zz':4},
    'in_subject' : {1 : '02', 2 : '01', 3 : '03', 7 : '04', 8 : '05', 6 : '06', 5 : '07', 4 : '08', 9 : '09'},
    'in_version' : {
        1 : '人教版',
        19 : '教科版',
        2 : '冀教版',
        3 : '北师大版',
        4 : '苏教版',
        5 : '浙教版',
        46: '北京课改版',
        99 : '青岛版',
        8 : '湘教版',
        32 : '沪教版',
        15 : '粤教版',
        88 : '人教新版'
    },
    'version' : {
        '人教版' : 1,
        '人教新版' : 88,
        '教科版' : 19,
        '冀教版' : 2,
        '北师大版': 3,
        '苏教版' : 4,
        '浙教版' : 5,
        '北京课改版' : 46,
        '青岛版' : 99,
        '湘教版' : 8,
        '沪教版' : 32,
        '粤教版' : 15,

        '人教旧版' : 777,
        '人教五四新版' : 777,
        '人教五四版' : 777,
        '浙教新版' : 777,
        '苏科新版' : 777,
        '湘教新版' : 777,
        '华师大版' : 777,
        '沪科新版' : 777,
        '翼教新版' : 777,
        '北京课改新版' : 777,
        '鲁教新版' : 777,
        '鲁教版' : 777,
        '外研新版' : 777,
        '牛津译林版' : 777,
        '牛津译林新版' : 777,
        '牛津上海版' : 777,
        '牛津深圳版' : 777,
        '仁爱新版' : 777,
        '仁爱版' : 777,
        '新世纪版' : 777,
        '教科新版' : 777,
        '沪外版' : 777,
        '鲁人版' : 777,
        '苏人版' : 777,
        '人民版' : 777,
        '陕教版' : 777,
        '湘师大版' : 777,
    }
}


db_host = '10.0.0.16'
db_port = 3306
db_user = 'efd_user'
db_name = 'efd_db'
db_passwd = 'hello1234'

Min_Question_Id = 70 * 10 * 10 * 10000 * 10000000

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

Url_Header = getUrlHeader('yt_header')