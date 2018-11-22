#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import json
import StringIO
import gzip
import time
import os

from yti import yt_config
from common.mysql_pool import Mysql_Pool
from common.http_util import Http_Pool
from common.http_util import urlParser
from common.log import Log

Common_Head = yt_config.getUrlHeader('yt_header')

COURSE_STR = 'COURSE'
TREEID_STR = 'TREEID'
IMAGE_STR = 'IMAGE'
Pic_Root = 'nqb'

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

def insert_version(data_dict):
    sql = 'insert into version_info(tree_id, course_id, course_name, version_name, publisher, subject,' \
          'version_id, gallery) ' \
          'values(%s, %s, %s, %s, %s, %s, %s, %s) ' \
          'on duplicate key update tree_id = %s, gallery = %s'
    # sql = 'insert ignore into version_info set %s '
    params = (data_dict['tree_id'], data_dict['course_id'], data_dict['course_name'], data_dict['version_name'],
              data_dict['publisher'], data_dict['subject'], data_dict['version_id'], data_dict['gallery'],
              data_dict['tree_id'], data_dict['gallery'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params)
    Mysql_Pool.get_conn().commit()
    cu.close()

def dispose_img(image_id, course_id):
    image_url = yt_config.Pic_Url.replace(IMAGE_STR, image_id)
    url_parser = urlParser(image_url)
    file_name = os.path.basename(url_parser.getPath())
    course_dir = yt_config.Store_Path + '/' + str(course_id)
    if not os.path.exists(course_dir):
        os.mkdir(course_dir)
    efd_file_path = os.path.join(course_dir, file_name)
    pic_header = yt_config.getUrlHeader('pic_header')
    if not os.path.exists(efd_file_path):
        fd = open(efd_file_path, 'wb')
        Http_Pool.create_client(yt_config.Pic_Host)
        try :
            Http_Pool.get_client().request("GET", image_url, '', pic_header)
        except:
            Log.error('error img_url:' + image_url)
            return
        response = Http_Pool.get_client().getresponse()
        if response.status != 200 :
            Log.error('pic down load failed!')
            Log.error('reason:' + response.reason)
            return
        fd.write(response.read())
        fd.close()
        Http_Pool.close_client()
    new_url = yt_config.Pics_Url_head + Pic_Root + '/' + str(course_id) + '/' + file_name
    return new_url

def dispose_gallery(galleries, course_id):
    for one in galleries:
        img_id = one['imageId']
        dispose_img(img_id, course_id)
        del one['imageId']
        one['image_id'] = img_id
        # one['name'] = one['name'].encode('utf-8')
    return galleries

#json.dumps(one_tree['gallery'], ensure_ascii=False,indent=2)
def download_version(url_parser, course):
    result_json = common_down(url_parser, None, 'GET')
    for one_tree in result_json:
        v_name = one_tree['name'].encode('utf-8')
        new_gallery = dispose_gallery(one_tree['gallery'], one_tree['courseId'])
        version_id = yt_config.compare_check['version'][v_name] if v_name in yt_config.compare_check['version'] else 777
        one_data = {
            'tree_id' : one_tree['id'],
            'course_id' : one_tree['courseId'],
            'course_name' : course,
            'version_name' : v_name,
            'publisher' : one_tree['description'],
            'subject' : yt_config.compare_check['subject'][course],
            'version_id' : version_id,
            'gallery' : json.dumps(new_gallery, ensure_ascii=False)
        }
        # insert_version(one_data)
        download_know_tree(one_tree['id'], course)
        time.sleep(3)
    print result_json

def insert_knowledge_tree(one_dict):
    sql = 'insert into knowledge_tree(id, name, parent_id, level, order_no, status, old_id, equal_parent) ' \
          ' values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update level = %s'
    # sql = 'insert ignore into version_info set %s '
    parameters = (one_dict['id'], one_dict['name'], one_dict['parent_id'],
                  one_dict['level'], one_dict['order_no'], one_dict['status'], one_dict['old_id'],
                  one_dict['equal_parent'], one_dict['level'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, parameters)
    Mysql_Pool.get_conn().commit()
    cu.close()

def download_know_tree(tree_id, course):
    know_url = yt_config.Know_Url.replace(COURSE_STR, course)
    know_url = know_url.replace(TREEID_STR, str(tree_id))
    know_url_parser = urlParser(know_url)
    result_js = common_down(know_url_parser, None, 'GET')
    l_one_order = 0
    for book in result_js['keypoints']:
        one_dict = {}
        one_dict['id'] = book['id']
        one_dict['name'] = book['name']
        one_dict['parent_id'] = tree_id
        one_dict['level'] = 1
        one_dict['status'] = 1
        one_dict['equal_parent'] = 0
        one_dict['old_id'] = book['count']
        one_dict['order_no'] = l_one_order
        l_one_order += 1
        insert_knowledge_tree(one_dict)
        l_two_order = 0
        for chapter in book['children']:
            one_dict = {}
            one_dict['id'] = chapter['id']
            one_dict['name'] = chapter['name']
            one_dict['parent_id'] = chapter['parentId']
            one_dict['level'] = 2
            one_dict['status'] = 1
            one_dict['equal_parent'] = 0
            one_dict['old_id'] = chapter['count']
            one_dict['order_no'] = l_two_order
            l_two_order += 1
            insert_knowledge_tree(one_dict)
            l_three_order = 0
            if not chapter['children']:
                continue
            for know in chapter['children']:
                one_dict = {}
                one_dict['id'] = know['id']
                one_dict['name'] = know['name']
                one_dict['parent_id'] = know['parentId']
                one_dict['level'] = 3
                one_dict['status'] = 1
                one_dict['equal_parent'] = 0
                one_dict['old_id'] = know['count']
                one_dict['order_no'] = l_three_order
                l_three_order += 1
                insert_knowledge_tree(one_dict)

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql(yt_config)
    # Wantu_File.initial()
    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    log_file = '/tmp/yt_know_' + str(grade_id)
    Log.init_log(log_file)

    for course in yt_config.compare_check['subject']:
        course_url = yt_config.Version_Url.replace(COURSE_STR, course)
        course_url_parser = urlParser(course_url)
        download_version(course_url_parser, course)
        time.sleep(5)

    Mysql_Pool.close_mysql()






