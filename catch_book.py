#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib, urllib
import mfg_config
import MySQLdb
import os
from crawl.common.http_util import Http_Pool
from crawl.common.http_util import urlParser
Date_Str = '1213'
Pic_Root = 'gfm'
from crawl.common.log import Log

Begin_Book_Id = 100



'''
   book_id                   int,
   create_time          timestamp default current_timestamp comment '创建时间',
   book_name                 varchar(100),
   book_version              varchar(100),
   pic                       varchar(200),
   grade_id             int,
   term_id                int,
   subject              int,
   old_id               varchar(30),
'''

def insert_book_info(conn, one_dict):
    global Begin_Book_Id
    conn.text_factory = str
    cu=conn.cursor()
    new_version = one_dict['version_id'] if one_dict['version_id'] > 9 else '9' + str(one_dict['version_id'])
    new_sub = one_dict['subject'] if one_dict['subject'] > 9 else '0' + str(one_dict['subject'])
    new_grade = one_dict['grade_id'] if one_dict['grade_id'] > 9 else '0' + str(one_dict['grade_id'])
    term_id = one_dict['term_id'] + 1

    if one_dict['grade_id'] > 9 :
        book_id = str(new_version) + str(new_sub) + str(Begin_Book_Id)
        Begin_Book_Id += 1
    else:
        book_id = str(new_version) + str(new_sub) + str(new_grade) + str(one_dict['term_id'] + 1)
    parameters = (book_id, one_dict['book_name'], one_dict['book_version'],
                  one_dict['pic'], one_dict['grade_id'],
                  one_dict['subject'], one_dict['old_id'], int(one_dict['version_id'], str(term_id)))

    sql = "insert into book_info(book_id, book_name, book_version, pic, grade_id, term_id, subject, old_id, version_id) " \
          "values (%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update term_id = %s "
    print 'insert book info one:' + sql % parameters
    cu.execute(sql, parameters)
    conn.commit()
    cu.close()

def dispose_img(img_url):
    url_parser = urlParser(img_url)
    file_name = os.path.basename(url_parser.getPath())
    efd_file_name = Date_Str + file_name
    efd_file_path = os.path.join(mfg_config.Store_Path, efd_file_name)
    pic_header = mfg_config.getUrlHeader('pic_header')
    if not os.path.exists(efd_file_path):
        fd = open(efd_file_path, 'wb')
        Http_Pool.create_client(url_parser.getHost())
        #conn = urllib.request.urlopen(url)
        try :
            Http_Pool.get_client().request("GET", img_url, '', pic_header)
        except:
            Log.error('error img_url:', img_url)

        response = Http_Pool.get_client().getresponse()
        if response.status != 200 :
            Log.error('pic down load failed!')
            Log.error('reason:' + response.reason)
        fd.write(response.read())
        fd.close()
        Http_Pool.close_client()
    new_url = mfg_config.Pics_Url_head + Pic_Root + '/' + efd_file_name
    return new_url

def dispose_booklist(connect, book_list):
    print 'book list is:', book_list
    one_book_dict = {}
    for one_book in book_list:
        one_book_dict['term_id'] = one_book['bookTerm']
        one_book_dict['book_version'] = one_book['bookVersion']
        new_img_url = dispose_img(one_book['pic'])
        one_book_dict['pic'] = new_img_url
        one_book_dict['old_id'] = one_book['bookId']
        one_book_dict['book_name'] = one_book['bookName']
        grade = one_book['grade']
        one_book_dict['grade_id'] = mfg_config.compare_check['grade'][grade]
        one_book_dict['subject'] = mfg_config.compare_check['subject'][one_book['subject']]
        if one_book['bookVersion'].find('人教') != -1:
            one_book_dict['version_id'] = 1
        else :
            try :
                version_id = int(one_book['bookVersionNumber'])
                one_book_dict['version_id'] = version_id
            except:
                Log.error('error book version:' + one_book['bookVersionNumber'])
                one_book_dict['version_id'] = 99

        insert_book_info(connect, one_book_dict)
        one_book_dict = {}

#subject=02&grade=c1&edution=0&science=2
if __name__ == '__main__':
    Log.init_log('/tmp/crawl_book.log')
    mysql_conn= MySQLdb.connect(
        host = mfg_config.db_host,
        port = mfg_config.db_port,
        user = mfg_config.db_user,
        passwd = mfg_config.db_passwd,
        db = mfg_config.db_name
        )
    httpClient = None
    params = {'subject': '09', 'grade': 'c1', 'edution' : '0', 'science' : '0'}
    headers = mfg_config.getUrlHeader('header')
    httpClient = httplib.HTTPConnection(mfg_config.Host, 80, timeout=30)

    url_parser = urlParser(mfg_config.Book_List_Path)
    for pr in params:
        url_parser.setParams(pr, params[pr])

    params_str = urllib.urlencode(url_parser.getParamsDict())

    Log.info('book url:' + url_parser.getFullUrl())
    httpClient.request("POST", url_parser.getFullUrl(), params_str, headers)

    response = httpClient.getresponse()
    if response.status != 200 :
        print 'Error Status!'
        print response.reason
    ret_str = response.read()
    try :
        one = eval(ret_str)
    except:
        print "error str:" + ret_str
    #print response.getheaders() #获取头信息
    for i in range(0, len(one['result'])):
        dispose_booklist(mysql_conn, one['result'][i]['bookList'])


