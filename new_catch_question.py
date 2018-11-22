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
Old_To_Bookid = {}
Know_Catch_Times = 2
Version_Id = 1

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

def dispose_img(html_body, grade_id):
    new_html = html_body
    img_list = re.findall(r'src=\"(http://pic\d+.mofangge.com[^\"]*?)\"', html_body)
    pic_header = mfg_config.getUrlHeader('pic_header')
    for img_url in img_list:
        url_parser = urlParser(img_url)
        file_name = os.path.basename(url_parser.getPath())
        efd_file_name = Date_Str + file_name
        efd_file_path = os.path.join(mfg_config.Store_Path, str(grade_id) ,efd_file_name)
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
        new_url = mfg_config.Pics_Url_head + Pic_Root + '/' + str(grade_id) + '/' + efd_file_name
        new_html = new_html.replace(img_url, new_url)
    return new_html

def insert_one(one_question):
    new_body_html = dispose_img(one_question['question_body_html'], one_question['grade_id'])
    new_body_html = new_body_html.replace('摩方格', '')
    new_analysis = dispose_img(one_question['answer_analysis'], one_question['grade_id'])
    new_analysis = new_analysis.replace('background: #0ea3f9;color:#ffffff', 'color:#000000')
    new_analysis = new_analysis.replace('摩方格', '')
    content = {
         'question_body' : '',
         'question_body_html' : new_body_html,
         'answer_analysis' : new_analysis
    }
    if new_analysis == '':
        one_question['question_head'] = 'null'
        Log.error('q_id no answer analysis! question_id:' + str(one_question['question_id']))
    json_str = json.dumps(content, ensure_ascii=False,indent=2)
    one_question['content'] = json_str
    sql = 'insert into question_bank(question_id, question_tag, content, question_answer, subject, type,' \
          ' question_head, grade_id, options, old_id, term_id, book_id) ' \
          'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
          ' on duplicate key update grade_id = %s, term_id = %s, old_id = %s, content = %s, book_id = %s'
    params_con = (one_question['question_id'], one_question['question_tag'], one_question['content'],
               one_question['question_answer'], one_question['subject'], one_question['type'],
               one_question['question_head'], one_question['grade_id'],
               one_question['options'], one_question['old_id'], one_question['term_id'], one_question['book_id'],
               one_question['grade_id'], one_question['term_id'], one_question['old_id'],
                 one_question['content'], one_question['book_id']
           )
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

def generate_quesiton_id(sub, grade_id, old_id, topic_id, term_id):
    new_sub = str(sub)
    grade_id += term_id
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
        return -1
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
                                               int(questions[q_id]['old_id']), q_id, questions[q_id]['term_id'])
        questions[q_id]['question_id'] = mfg_config.Min_Question_Id + long(question_id_str)
        questions[q_id]['book_id'] = book_id
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

def generate_record(name, old_id, parent_id, level, order):
    one_record = {}
    one_record['name'] = name
    one_record['old_id'] = old_id
    one_record['level'] = level
    one_record['status'] = 1
    one_record['order_no'] = order
    one_record['parent_id'] = parent_id
    return one_record

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
    cu.execute("insert into bak_know(id, name, parent_id, level, order_no, status, old_id, equal_parent)"
               " values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update level = %s, name = %s, "
               "old_id = %s, equal_parent = %s ",
               parameters)
    conn.commit()
    cu.close()
    return id

def dispose_knowledge_list(know_list, parent_id, know_params, e_book_id):
    order = 1
    for one_book in know_list:
        one_record = generate_record(one_book['pointName'], one_book['pointId'], parent_id, 2, order)
        one_record['equal_parent'] = 0
        order += 1
        kid = insert_knowledge_tree(one_record)
        Know_Tree.add_node(parent_id, kid, one_record['name'], 2, one_record['old_id'])

        d_know_params = {
            'grade' : know_params['grade'],
            'sub' : know_params['subject'],
            'knowId': one_record['old_id']
        }

        for i in range(0, Know_Catch_Times):
            if down_know_id(d_know_params, kid, e_book_id) < 0:
                    Log.error('download k_id:' + kid + ' failed! ')

def crawl_knows(know_params, efd_chapter_id, e_book_id):
    url_parser = urlParser(mfg_config.Knowledge_Path)
    for pr in know_params:
        url_parser.setParams(pr, know_params[pr])
    result_json = common_down(url_parser)
    know_list = result_json['result']['knowledgeList']
    dispose_knowledge_list(know_list, efd_chapter_id, know_params, e_book_id)

def dispose_chapter_list(chapter_list, e_book_id, chapter_params):
    order = 1
    chapter_ids = {}
    for one_book in chapter_list:
        one_record = generate_record(one_book['chapterName'], one_book['chapterId'], e_book_id, 1, order)
        one_record['equal_parent'] = 0
        order += 1
        id = insert_knowledge_tree(one_record)
        Know_Tree.add_node(e_book_id, id, one_record['name'], 1, one_record['old_id'])
        chapter_ids[one_book['chapterId']] = id

    for (c_id, e_c_id) in chapter_ids.items():
        Log.info('%s:%s' %(c_id, e_c_id))
        time.sleep(1)
        know_parasm = {
            'chapterid' : c_id,
            'grade' : chapter_params['grade'],
            'subject' : chapter_params['subject'],
        }
        crawl_knows(know_parasm, e_c_id, e_book_id)


def get_efd_book_id(book_list):
    for one_book in book_list:
        if one_book['isSelect'] == True:
            e_subject = mfg_config.compare_check['subject'][one_book['subject']]
            old_book_ky = one_book['bookId'] + '_' + str(e_subject)
            if old_book_ky in Old_To_Bookid:
                return Old_To_Bookid[old_book_ky]
    return None

def get_select_book(book_list):
    for one_book in book_list:
        if one_book['isSelect'] == True:
            return one_book
    return None

def insert_new_book(subject, grade_id, term_id, old_id, book_name):
    conn = Mysql_Pool.get_conn()
    conn.text_factory = str
    cu=conn.cursor()
    new_version = str(Version_Id) if Version_Id > 9 else '9' + str(Version_Id)
    new_sub = str(subject) if subject > 9 else '0' + str(subject)
    new_grade = str(grade_id) if grade_id > 9 else '0' + str(grade_id)
    if book_name == '高考':
        new_grade = '88'
    new_term = str(term_id)
    book_id = new_version + new_sub + new_grade + new_term
    parameters = (book_id, book_name, '', '', grade_id, term_id,
                  subject, old_id, Version_Id, term_id)


    sql = "insert into book_info(book_id, book_name, book_version, pic, grade_id, " \
          "term_id, subject, old_id, version_id) " \
          "values (%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update term_id = %s"
    print 'insert book info one:' + sql % parameters
    cu.execute(sql, parameters)
    conn.commit()
    cu.close()
    one = {'book_id' : book_id, 'old_id' : old_id,
           'book_name' : book_name, 'subject' : subject,
           'grade_id': grade_id, 'term_id' : term_id}
    Books_Info[book_id] = one
    Old_To_Bookid[old_id + '_' + str(subject)] = book_id
    return book_id

def crawl_first_book(chapter_params):
    url_parser = urlParser(mfg_config.Text_Book_Chapter)
    for pr in chapter_params:
        url_parser.setParams(pr, chapter_params[pr])
    result_json = common_down(url_parser)
    if result_json['status'] != '11-001':
        Log.error(url_parser.getFullUrl() + ' failed!')
        return -1
    book_list = result_json['result']['bookList']
    efd_book_id = get_efd_book_id(book_list)
    choosed_book = get_select_book(book_list)
    chapter_params['term'] = choosed_book['term']
    if efd_book_id is None:
        Log.error('no book select in booklist:' + str(book_list))
        e_subject = mfg_config.compare_check['subject'][choosed_book['subject']]
        e_grade_id = mfg_config.compare_check['grade'][chapter_params['grade']]
        efd_book_id = insert_new_book(e_subject, e_grade_id, 9,
                                      choosed_book['bookId'], choosed_book['termName'])

    chapter_list = result_json['result']['chapterList']
    if chapter_list is None:
        Log.error("get chapter list failed!")
        Log.error(result_json)
    dispose_chapter_list(chapter_list, efd_book_id, chapter_params)
    return book_list

def crawl_one_book(get_params, choosed_book):
    url_parser = urlParser(mfg_config.Book_Chapter)
    for pr in get_params:
        url_parser.setParams(pr, get_params[pr])
    result_json = common_down(url_parser)
    e_subject = mfg_config.compare_check['subject'][choosed_book['subject']]
    old_book_ky = get_params['bookid'] + '_' + str(e_subject)
    if old_book_ky in Old_To_Bookid:
        efd_book_id = Old_To_Bookid[old_book_ky]
    else:
        Log.error('no found e_book_id:' + get_params['bookid'])
        e_subject = mfg_config.compare_check['subject'][choosed_book['subject']]
        e_grade_id = mfg_config.compare_check['grade'][get_params['grade']]
        efd_book_id = insert_new_book(e_subject, e_grade_id, 9,
                                      choosed_book['bookId'], choosed_book['termName'])
    chapter_list = result_json['result']
    if chapter_list is None:
        Log.error("get chapter list failed!")
        Log.error(result_json)
    dispose_chapter_list(chapter_list, efd_book_id, get_params)

def dispose_books(books, subject, old_grade):
    first_book_id = list(books)[0]
    old_book_id = books[first_book_id]['old_id']
    #book_name = books[first_book_id]['book_name']
    #if book_name == '中考' or book_name == '高考' or book_name = '':
    term = old_book_id[-1:]
    chapter_params = {'bookId' : old_book_id,
          'subject' : subject,
          'grade' : old_grade,
          'term' : term
          }
    book_list = crawl_first_book(chapter_params)

    for book in book_list:
        if book['isSelect'] == False:
            crawl_params = {'bookid' : book['bookId'],
              'subject' : subject,
              'grade' : old_grade,
              'term' : book['term']
              }
            Log.info('now catch book:' + str(book))
            crawl_one_book(crawl_params, book)

def get_book_ids(subject, grade_id, book_id = None):
    books = {}
    conn = Mysql_Pool.get_conn()
    sql = 'select * from book_info where version_id = ' + str(Version_Id) + ' and subject = ' + str(subject)
    if grade_id < 10:
        sql += ' and grade_id = ' + str(grade_id)
    else :
        sql += ' and grade_id in (10, 11, 12)'
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    for one in cu.fetchall():
        books[one['book_id']] = one
        Books_Info[one['book_id']] = one
        Old_To_Bookid[one['old_id'] + '_' + str(one['subject'])] = one['book_id']
    cu.close()
    return books

def get_subjects(grade_id):
    if grade_id < 7:
        return ['02', '01', '03']
    elif grade_id < 10:
        return ['02', '09', '04', '05', '08', '07','01', '03', '07']
    elif grade_id < 13:
        return ['02', '08', '09', '07', '03', '01', '04', '05', '06']
    else :
        return []

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    Wantu_File.initial()
    initial_knowledge()

    if len(sys.argv) > 1:
        grade_id = int(sys.argv[1])
    else :
        grade_id = 9

    a_book_id = None
    if len(sys.argv) > 2:
        a_book_id = int(sys.argv[2])

    log_file = '/tmp/crawl.log_normal_' + str(grade_id)
    Log.init_log(log_file)
    subjects = get_subjects(grade_id)
    old_grade = mfg_config.compare_check['in_grade'][grade_id]

    for subject in subjects:
        efd_subject = mfg_config.compare_check['subject'][subject]
        books = get_book_ids(efd_subject, grade_id, a_book_id)
        if len(books) == 0:
            continue
        dispose_books(books, subject, old_grade)

    Mysql_Pool.close_mysql()