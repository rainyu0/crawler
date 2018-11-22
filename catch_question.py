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

import mfg_config
from crawl.common.mysql_pool import Mysql_Pool
from crawl.common.wantu_file import Wantu_File
from crawl.common.http_util import Http_Pool
from crawl.common.http_util import urlParser
from crawl.common.tree_manager import Tree_Manager
from crawl.common.log import Log

Know_Tree = Tree_Manager()
#Date_Str = time.strftime('%Y%m%d')
Date_Str = '1213'
Pic_Root = 'gfm'
Common_Head = mfg_config.getUrlHeader('header')
Books_Info = {}

def initial_knowledge():
    conn = Mysql_Pool.get_conn()
    sql = 'select * from knowledge_tree order by level asc'
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    for one in know_cursor.fetchall():
        Know_Tree.add_node(one['parent_id'], one['id'], one['name'], one['level'], one['old_id'])

def random_answer():
    chars = 'ABCD'
    length = len(chars) - 1
    random = Random()
    ch_str = chars[random.randint(0, length)]
    return ch_str

def constribute_question_result(questions):
    ret_str = ''
    for q_id in questions:
        use_time = Random().randint(1, 4)
        q_str = str(q_id) + ',' + random_answer() + ',' + str(use_time)
        ret_str += q_str + '|'
    return ret_str[0:-1]

#673747,False,A,B|731268,False,D,B|
def get_true_answers(questions, answers_str):
    answers = answers_str.split('|')
    for answer in answers:
        items = answer.split(',')
        q_id = int(items[0])
        questions[q_id]['question_answer'] = items[2]

def down_answer_analysis(get_params):
    url_parser = urlParser(mfg_config.answer_analysis_path)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    result_json = common_down(url_parser)
    return result_json['result']

def down_answers(questions, get_params):
    url_parser = urlParser(mfg_config.question_answer_path)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    user_answers = constribute_question_result(questions)
    url_parser.setParams('questionResult', user_answers)
    # mock answer
    time.sleep(2)
    result_json = common_down(url_parser)
    if result_json['status'] != '11-001':
        Log.error('download question answers failed:' + url_parser.getFullUrl())
        return -1
    question_answer = result_json['result']['questionResult']
    get_true_answers(questions, question_answer)
    for q_id in questions:
        time.sleep(0.3)
        analysis_params = {'sub' : get_params['subjectId'], 'topicId' : q_id}
        try :
            questions[q_id]['answer_analysis'] = down_answer_analysis(analysis_params)
        except :
            questions[q_id]['answer_analysis'] = ''
            Log.error('Error! get answer analysis failed!')
            time.sleep(20)
    return 0

def dispose_img(html_body):
    new_html = html_body
    img_list = re.findall(r'src=\"(http://pic\d+.mofangge.com[^\"]*?)\"', html_body)
    pic_header = mfg_config.getUrlHeader('pic_header')
    for img_url in img_list:
        url_parser = urlParser(img_url)
        file_name = os.path.basename(url_parser.getPath())
        efd_file_name = Date_Str + file_name
        efd_file_path = os.path.join(mfg_config.Store_Path, efd_file_name)
        if not os.path.exists(efd_file_path):
            fd = open(efd_file_path, 'wb')
            Http_Pool.create_client(url_parser.getHost())
            #conn = urllib.request.urlopen(url)
            try :
                Http_Pool.get_client().request("GET", img_url, '', pic_header)
            except:
                Log.error('error img_url:' + img_url)
                continue
            response = Http_Pool.get_client().getresponse()
            if response.status != 200 :
                Log.error('pic down load failed!')
                Log.error('reason:' + response.reason)
                continue
            fd.write(response.read())
            fd.close()
            Http_Pool.close_client()
            #Wantu_File.initial()
            #new_url = Wantu_File.upload_file(efd_file_path, Pic_Root)
        new_url = mfg_config.Pics_Url_head + Pic_Root + '/' + efd_file_name
        new_html = new_html.replace(img_url, new_url)
    return new_html

def insert_one(one_question):
    new_body_html = dispose_img(one_question['question_body_html'])
    new_analysis = dispose_img(one_question['answer_analysis'])
    new_analysis = new_analysis.replace('background: #0ea3f9;color:#ffffff', 'color:#000000')
    content = {
         'question_body' : '',
         'question_body_html' : new_body_html,
         'answer_analysis' : new_analysis
    }
    if new_analysis == '':
        one_question['question_head'] = 'null'
        Log.error('q_id no answer analysis! question_id:' + one_question['question_id'])
    json_str = json.dumps(content, ensure_ascii=False,indent=2)
    one_question['content'] = json_str
    sql = 'insert into question_bank(question_id, question_tag, content, question_answer, subject, type,' \
          ' question_head, grade_id, options, old_id, term_id) ' \
          'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
          ' on duplicate key update grade_id = %s, term_id = %s, old_id = %s, content = %s'
    params_con = (one_question['question_id'], one_question['question_tag'], one_question['content'],
               one_question['question_answer'], one_question['subject'], one_question['type'],
               one_question['question_head'], one_question['grade_id'],
               one_question['options'], one_question['old_id'], one_question['term_id'],
               one_question['grade_id'], one_question['term_id'], one_question['old_id'],
                 one_question['content']
           )
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

# def batch_insert(questions):
#     for q_id in questions:
#         new_body_html = dispose_img(questions[q_id]['question_body_html'])
#         new_analysis = dispose_img(questions[q_id]['answer_analysis'])
#         content = {
#              'question_body' : '',
#              'question_body_html' : new_body_html,
#              'answer_analysis' : new_analysis
#         }
#         if new_analysis == '':
#             questions[q_id]['question_head'] = 'null'
#             Log.error('q_id no answer analysis!' + str(q_id))
#         json_str = json.dumps(content, ensure_ascii=False,indent=2)
#         questions[q_id]['content'] = json_str
#     sql = 'insert into question_bank(question_id, question_tag, content, question_answer, subject, type,' \
#           ' question_head, grade_id, options, old_id, term_id) ' \
#           'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
#           ' on duplicate key update grade_id = grade_id, term_id = term_id, old_id = old_id '
#     all_questions = []
#     for q_id in questions:
#         one = (questions[q_id]['question_id'], questions[q_id]['question_tag'], questions[q_id]['content'],
#                questions[q_id]['question_answer'], questions[q_id]['subject'], questions[q_id]['type'],
#                questions[q_id]['question_head'], questions[q_id]['grade_id'],
#                questions[q_id]['options'], questions[q_id]['old_id'], questions[q_id]['term_id'])
#         all_questions.append(one)
#
#     cu = Mysql_Pool.get_conn().cursor()
#     cu.executemany(sql, all_questions)
#     Mysql_Pool.get_conn().commit()
#     cu.close()

def generate_quesiton_id(sub, grade_id, old_id, topic_id):
    new_sub = str(sub)
    new_grade = str(grade_id) if grade_id > 9 else '0' + str(grade_id)
    new_old_id = str(old_id) if old_id > 999 else '0' + str(old_id)
    new_top_id = str(topic_id) if topic_id > 999999 else '0' + str(topic_id)
    return new_sub + new_grade + new_old_id + new_top_id

def down_know_id(params, k_id, book_id):
    url_parser = urlParser(mfg_config.question_dettail_path)
    for pr in params:
        url_parser.setParams(pr, params[pr])
    result_json = common_down(url_parser)
    if result_json['status'] != '11-001':
        Log.error('download question detail k_id:' + str(k_id) + ' failed! ')
        return -1
    question_list = result_json['result']['questionList']
    if question_list is None:
        Log.error("get question list failed!")
        Log.error(result_json)
    questions = {}
    for one_quesion in question_list:
        q_id = one_quesion['id']
        questions[q_id] = {}
        questions[q_id]['question_body_html'] = one_quesion['body']
        questions[q_id]['options'] = one_quesion['option']
        sub = params['sub']
        questions[q_id]['subject'] = mfg_config.compare_check['subject'][sub]
        grade = params['grade']
        questions[q_id]['grade_id'] = Books_Info[book_id]['grade_id']
        questions[q_id]['knowledge_id']= k_id
        questions[q_id]['question_tag'] = Know_Tree.get_name(k_id)
        questions[q_id]['type'] = 1
        questions[q_id]['question_head'] = ''
        questions[q_id]['old_id'] = params['knowId']
        questions[q_id]['term_id'] = Books_Info[book_id]['term_id']
        question_id_str = generate_quesiton_id(questions[q_id]['subject'], questions[q_id]['grade_id'],
                                               int(questions[q_id]['old_id']), q_id)
        questions[q_id]['question_id'] = mfg_config.Min_Question_Id + long(question_id_str)
    parent_id = Know_Tree.get_parent_id(k_id)
    chapter_id = Know_Tree.get_old_id(parent_id)
    get_answer_params = {'chapterId' : chapter_id,
              'knowid' : Know_Tree.get_old_id(k_id),
              'grade' : params['grade'],
              'subjectId' : params['sub'],
              }
    if down_answers(questions, get_answer_params) < 0:
        return -1
    for q_id in questions:
        insert_one(questions[q_id])
    #batch_insert(questions)
    return 0

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
    chapter_json = json.loads(ret_str, encoding="utf-8")
    Http_Pool.close_client()
    return chapter_json

def get_book_ids(version_id, subject):
    books = {}
    conn = Mysql_Pool.get_conn()
    sql = 'select * from book_info where version_id = ' + str(version_id) + ' and subject = ' + str(subject)
    #sql += ' and grade_id = 7'
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    for one in know_cursor.fetchall():
        books[one['book_id']] = one
    return books

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    Wantu_File.initial()
    log_file = '/tmp/crawl.log_normal'
    # pro_path = sys.argv[0]
    # file_name = os.path.dirname(pro_path)
    # file_name = os.path.dirname(file_name)
    # file_name = os.path.basename(file_name)
    # log_file += '_' + file_name
    Log.init_log(log_file)

    version = 1
    subject = '02'
    if len(sys.argv) > 0:
        subject = sys.argv[1]
    efd_subject = mfg_config.compare_check['subject'][subject]
    Books_Info = get_book_ids(version, efd_subject)
    Log.info('all books:' + str(Books_Info))
    for book_id in Books_Info:
        time.sleep(5)
        old_book_id = Books_Info[book_id]['old_id']
        grade = old_book_id[-3:-1]
        if grade == '00' or old_book_id.find('g') != -1:
            grade = 'g1'
        common_params = {'grade' : grade,
                         'sub' : subject}
        initial_knowledge()
        know_nodes = Know_Tree.get_nodes_by_level(book_id, 2)
        Log.info('all_know_ids:' + str(know_nodes))
        all_knows = []
        for k_id in know_nodes:
            all_knows.append(k_id)

        random.shuffle(all_knows)
        for k_id in all_knows:
            time.sleep(1)
            remote_id = Know_Tree.get_old_id(k_id)
            if not remote_id or len(remote_id) < 2:
                continue
            common_params['knowId'] = remote_id
            if down_know_id(common_params, k_id, book_id) < 0:
                Log.error('download k_id:' + str(k_id) + ' failed! ')
                continue
            # try :
            #     down_know_id(common_params, k_id)
            # except:
            #     Log.error('download k_id:' + str(k_id) + ' failed! ')
            #     time.sleep(5)
    Mysql_Pool.close_mysql()