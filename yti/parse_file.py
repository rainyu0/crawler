#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import json
import StringIO
import gzip
import time
import re
import os
from urllib import unquote

from yti import yt_config
from common.mysql_pool import Mysql_Pool
from common.log import Log
import common.utils as utils
from common.http_util import urlParser
from common.http_util import Http_Pool
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

File_Root = '/Users/shengyu/tmp/yt/www.yuantiku.com/android'
IMAGE_STR = 'IMAGE'
Pic_Header = yt_config.getUrlHeader('pic_header')

def get_define_dir(path, pattern):
    d = []
    course_list = os.listdir(path)
    for c_dir in course_list:
        c_path = path + '/' + c_dir
        if c_dir.find(pattern) != -1:
            d.append(c_path)
    return d

def get_data_file(path):
    file_list = []
    question_dir = get_define_dir(path, 'questions')
    if len(question_dir) == 0:
        print 'Error, no questions dir'
        return file_list
    return get_define_dir(question_dir[0], 'bundle')

def get_tree_id(f_name):
    img_list = re.findall(r'treeId=(\d+)', f_name)
    if len(img_list) > 0:
        return img_list[0]
    return None

def get_paper_id(f_name):
    img_list = re.findall(r'exerciseId=(\d+)', f_name)
    if len(img_list) > 0:
        return img_list[0]
    return None

def insert_question(data_dict):
    sql = 'insert into n_q_bank(q_id, update_time, content, solution, material_id, ' \
          'type, difficulty, accessories, note, key_points,' \
          ' solution_access, question_meta, source, tree_id, correct_answer, ' \
          'subject) ' \
          'values(%s, now(), %s, %s, %s, ' \
          '%s, %s, %s, %s, %s,' \
          '%s, %s, %s, %s, %s, ' \
          '%s) ' \
          'on duplicate key update tree_id = %s, update_time = now()'
    params = (data_dict['q_id'], data_dict['content'], data_dict['solution'], data_dict['material_id'],
              data_dict['type'], data_dict['difficulty'], data_dict['accessories'], data_dict['note'], data_dict['key_points'],
              data_dict['solution_access'], data_dict['question_meta'], data_dict['source'], data_dict['tree_id'], data_dict['correct_answer'],
              data_dict['subject'], data_dict['tree_id'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params)
    Mysql_Pool.get_conn().commit()
    cu.close()

def insert_material(data_dict):
    sql = 'insert into material(id, update_time, content, accessories, question_ids, tree_id, subject)' \
          'values(%s, %s, %s, %s, %s, ' \
          '%s, %s) ' \
          'on duplicate key update update_time = now()'
    params = (data_dict['id'], 'now()', data_dict['content'], data_dict['accessories'], data_dict['question_ids'],
              data_dict['tree_id'], data_dict['subject'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params)
    Mysql_Pool.get_conn().commit()
    cu.close()

def insert_paper(data_dict):
    sql = 'insert into paper(id, update_time, question_ids, tree_id, subject, key_points)' \
          'values(%s, now(), %s, %s, %s, %s) ' \
          'on duplicate key update update_time = now(), question_ids = %s '
    params = (data_dict['id'], data_dict['question_ids'],
              data_dict['tree_id'], data_dict['subject'], data_dict['key_points'],
              data_dict['question_ids'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params)
    Mysql_Pool.get_conn().commit()
    cu.close()

def dispose_content(content, subject):
    new_content = content
    tex_list = re.findall(r'\[tex=[^\]]*\]([^\[]*)', new_content)
    img_list = re.findall(r'\[img=[^\]]*\]([^\[]*)', new_content)

    for img_id in img_list:
        subject_dir = yt_config.Store_Path + '/' + str(subject)
        if not os.path.exists(subject_dir):
            os.mkdir(subject_dir)
        efd_file_path = os.path.join(subject_dir, img_id)
        if os.path.exists(efd_file_path):
            continue
        if img_id.endswith('png') or img_id.endswith('jpg'):
            pic_url = yt_config.Png_Pic_Url.replace(IMAGE_STR, img_id)
        if img_id.endswith('svg'):
            pic_url = yt_config.SVG_Pic_Url.replace(IMAGE_STR, img_id)
        fd = open(efd_file_path, 'wb')
        Http_Pool.create_client(yt_config.Pic_Host)
        try :
            Http_Pool.get_client().request("GET", pic_url, '', Pic_Header)
        except:
            Log.error('error img_url:' + pic_url)
            continue
        response = Http_Pool.get_client().getresponse()
        if response.status != 200 :
            Log.error('pic down load failed!')
            Log.error('reason:' + response.reason)
            continue
        fd.write(response.read())
        fd.close()
        Http_Pool.close_client()

    for tex_str in tex_list:
        Http_Pool.create_client(yt_config.Tex_Host, yt_config.Tex_Port)
        tex_url = yt_config.Tex_Url.replace(IMAGE_STR, tex_str)
        try :
            Http_Pool.get_client().request("GET", tex_url, '', Pic_Header)
            response = Http_Pool.get_client().getresponse()
        except:
            Log.error('error img_url:' + tex_url)
            continue
        if response.status != 200 :
            Log.error('tex load failed!' + tex_str)
            continue
        new_tex = response.read()[2:-3]
        new_content = new_content.replace(tex_str, new_tex)
    return new_content

def dispose_file(d_file, subject):
    f_name = os.path.basename(d_file)
    u_name = unquote(f_name)
    print u_name
    tree_id = get_tree_id(u_name)
    if tree_id is None:
        print 'Error. Not found tree id'
    if not os.path.exists(d_file):
        return
    fd = open(d_file, 'r')
    all_text = fd.read()
    # new_text = dispose_content(all_text, subject)
    try :
        data_js = json.loads(all_text)
    except IOError, e:
        print "json load failed! file:" + d_file, e
        return
    fd.close()
    paper_data = {}
    paper_data['id'] = int(get_paper_id(u_name))
    question_ids = []
    for question in data_js['questions']:
        one_data = {}
        one_data['tree_id'] = tree_id
        one_data['subject'] = subject
        one_data['q_id'] = utils.generate_yt_id(subject, tree_id, question['id'])
        one_data['content'] = dispose_content(question['content'], subject)
        one_data['solution'] = dispose_content(question['solution'], subject)
        one_data['material_id'] = question['materialId']
        one_data['type'] =question['type']
        one_data['difficulty'] = question['difficulty']
        one_data['source'] = question['source']
        one_data['tree_id'] = tree_id
        access_str = json.dumps(question['accessories'], ensure_ascii=False)
        try:
            one_data['accessories'] = dispose_content(access_str, subject)
        except Exception, e:
            print access_str, e
            pass
        one_data['correct_answer'] = json.dumps(question['correctAnswer'], ensure_ascii=False)
        one_data['key_points'] = json.dumps(question['keypoints'], ensure_ascii=False)
        one_data['question_meta'] = json.dumps(question['questionMeta'], ensure_ascii=False)
        one_data['solution_access'] = json.dumps(question['solutionAccessories'], ensure_ascii=False)
        one_data['note'] = question['note']
        insert_question(one_data)
        question_ids.append(one_data['q_id'])
        paper_data['key_points'] = one_data['key_points']
    paper_data['question_ids'] = ','.join(question_ids)
    paper_data['tree_id'] = tree_id
    paper_data['subject'] = subject
    insert_paper(paper_data)

    for material in data_js['materials']:
        one_data = {}
        one_data['id'] = material['id']
        one_data['content'] = dispose_content(material['content'],  subject)
        one_data['accessories'] = utils.list_to_str(material['accessories'])
        one_data['question_ids'] = utils.list_to_str(material['questionIds'])
        one_data['tree_id'] = tree_id
        one_data['subject'] = subject
        insert_material(one_data)
    print data_js

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql(yt_config)
    # Wantu_File.initial()
    Log.init_log()
    p_str = 'cz'
    course_paths = get_define_dir(File_Root, p_str)
    for c_path in course_paths:
        print 'cz path:' + c_path
        file_list = get_data_file(c_path)
        sub = os.path.basename(c_path)[-2:]
        subject = yt_config.compare_check['subject'][sub]
        for fl in file_list:
            dispose_file(fl, subject)
    Mysql_Pool.close_mysql()

