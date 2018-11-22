#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import httplib
import urllib
import json
import time
import MySQLdb

import mfg_config
from crawl.common.mysql_pool import Mysql_Pool
from crawl.common.http_util import Http_Pool
from crawl.common.http_util import urlParser
from crawl.common.log import Log

Common_Head = mfg_config.getUrlHeader('header')
Books_Info = {}
Old_To_Bookid = {}

'''
   id                   int not null,
   name                 varchar(200),
   parent_id            int,
   level                int,
   create_time          timestamp default current_timestamp comment '创建时间',
   order_no             int comment '序号',
   status               int(1) comment '状态',
   old_id               varchar(30),
   expression           varchar(50),
   equal_parent         int default 0 comment '是否等同于parent_id, 用于总复习',
   primary key (id)
'''
def insert_knowledge_tree(one_dict):
    conn = Mysql_Pool.get_conn()
    conn.text_factory = str
    cu=conn.cursor()
    sub_id_str = str(one_dict['order_no']) if one_dict['order_no'] > 9 else '0' + str(one_dict['order_no'])
    id = str(one_dict['parent_id']) + sub_id_str
    parameters = (id, one_dict['name'], one_dict['parent_id'],
                  one_dict['level'], one_dict['order_no'], one_dict['status'], one_dict['old_id'],
                  one_dict['equal_parent'], one_dict['level'], one_dict['name'], one_dict['old_id'],  one_dict['equal_parent'])
    Log.info('insert know record:' + str(parameters))
    cu.execute("insert into knowledge_tree(id, name, parent_id, level, order_no, status, old_id, equal_parent)"
               " values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update level = %s, name = %s, "
               "old_id = %s, equal_parent = %s ",
               parameters)
    conn.commit()
    cu.close()
    return id

def dispose_chapter_list(chapter_list, parent_id):
    order = 1
    chapter_ids = {}
    for one_book in chapter_list:
        one_record = generate_record(one_book['chapterName'], one_book['chapterId'], parent_id, 1, order)
        one_record['equal_parent'] = 0
        order += 1
        id = insert_knowledge_tree(one_record)
        chapter_ids[one_book['chapterId']] = id

    for (c_id, e_c_id) in chapter_ids.items():
        Log.info('%s:%s' %(c_id, e_c_id))
        time.sleep(1)
        know_parasm = {
            'chapterid' : c_id,
            'grade' : common_params['grade'],
            'subject' : common_params['subject'],
        }
        crawl_one_chapter(know_parasm, e_c_id)

def generate_record(name, old_id, parent_id, level, order):
    one_record = {}
    one_record['name'] = name
    one_record['old_id'] = old_id
    one_record['level'] = level
    one_record['status'] = 1
    one_record['order_no'] = order
    one_record['parent_id'] = parent_id
    return one_record

def dispose_knowledge_list(know_list, parent_id):
    order = 1
    for one_book in know_list:
        one_record = generate_record(one_book['pointName'], one_book['pointId'], parent_id, 2, order)
        one_record['equal_parent'] = 0
        order += 1
        insert_knowledge_tree(one_record)

def crawl_one_chapter(get_params, efd_chapter_id):
    url_parser = urlParser(mfg_config.Knowledge_Path)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    result_json = common_down(url_parser)
    know_list = result_json['result']['knowledgeList']
    dispose_knowledge_list(know_list, efd_chapter_id)

def get_efd_book_id(book_list):
    for one_book in book_list:
        if one_book['isSelect'] == True:
            old_id = one_book['bookId']
            return Old_To_Bookid[old_id]
    return None

def crawl_first_book(get_params):
    url_parser = urlParser(mfg_config.Text_Book_Chapter)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    result_json = common_down(url_parser)
    book_list = result_json['result']['bookList']
    efd_book_id = get_efd_book_id(book_list)
    chapter_list = result_json['result']['chapterList']
    if chapter_list is None:
        Log.error("get chapter list failed!")
        Log.error(result_json)
    dispose_chapter_list(chapter_list, efd_book_id)
    return book_list

def crawl_one_book(get_params):
    url_parser = urlParser(mfg_config.Book_Chapter)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    result_json = common_down(url_parser)
    efd_book_id = Old_To_Bookid[get_params['bookid']]
    chapter_list = result_json['result']
    if chapter_list is None:
        Log.error("get chapter list failed!")
        Log.error(result_json)
    dispose_chapter_list(chapter_list, efd_book_id)


def common_down(url_parser):
    Http_Pool.create_client()
    params = urllib.urlencode(url_parser.getParamsDict())
    full_url = url_parser.getFullUrl()
    Log.info('http request:' + full_url)
    content_length = len(params)
    Common_Head['Content-Length'] = content_length
    Http_Pool.get_client().request("POST", full_url, params, Common_Head)
    response = Http_Pool.get_client().getresponse()
    if response.status != 200 :
        Log.error('Error Status!')
        Log.error(response.reason)
    ret_str = response.read()
    result_json = json.loads(ret_str, encoding="utf-8")
    Http_Pool.close_client()
    return result_json

# def get_book_ids(version_id, subject, grade_id):
#     books = {}
#     conn = Mysql_Pool.get_conn()
#     sql = 'select * from book_info where version_id = ' + str(version_id) + ' and subject = ' + str(subject)
#     # TODO : delete it
#     sql += ' and grade_id = ' + str(grade_id)
#     know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
#     know_cursor.execute(sql, [])
#     for one in know_cursor.fetchall():
#         books[one['book_id']] = one['old_id']
#     return list(books)

def get_book_ids(version_id, subject, grade_id):
    books = {}
    conn = Mysql_Pool.get_conn()
    sql = 'select * from book_info where version_id = ' + str(version_id) + ' and subject = ' + str(subject)
    sql += ' and grade_id = ' + str(grade_id)
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    for one in know_cursor.fetchall():
        books[one['book_id']] = one
        Old_To_Bookid[one['old_id']] = one['book_id']
    return books


#subject=02&grade=c1&edution=0&science=2
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    log_file = '/tmp/crawl_know.log'
    Log.init_log(log_file)

    version = 1
    subject = '01'
    grade_id = 6
    efd_subject = mfg_config.compare_check['subject'][subject]
    Books_Info = get_book_ids(version, efd_subject, grade_id)
    Log.info('all books:' + str(Books_Info))
    first_book_id = list(Books_Info)[0]
    old_book_id = Books_Info[first_book_id]['old_id']
    term = old_book_id[-1:]
    grade = old_book_id[-3:-1]
    if grade == '00' or old_book_id.find('g') != -1:
        grade = 'g1'
    common_params = {'bookId' : old_book_id,
          'subject' : subject,
          'grade' : grade,
          'term' : term
          }
    book_list = crawl_first_book(common_params)

    for book in book_list:
        if book['isSelect'] == False:
            crawl_params = {'bookid' : book['bookId'],
              'subject' : subject,
              'grade' : grade,
              'term' : book['term']
              }
            crawl_one_book(crawl_params)
    Mysql_Pool.close_mysql()

