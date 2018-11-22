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
import shutil
from random import Random
import random
from bs4 import BeautifulSoup
import hashlib

import mfg_config
from crawl.common.mysql_pool import Mysql_Pool
from crawl.common.wantu_file import Wantu_File
from crawl.common.http_util import Http_Pool
from crawl.common.http_util import urlParser
from crawl.common.tree_manager import Tree_Manager
from crawl.common.log import Log

Know_Tree = Tree_Manager()
#Date_Str = time.strftime('%Y%m%d')
Pic_Root = 'qb'
Common_Head = mfg_config.getUrlHeader('header')
Books_Info = {}
Old_To_Bookid = {}
VersionId_VerName = {}
# Validate_Versions =  {
#          1 : '人教版',
#         19 : '教科版',
#         2 : '冀教版',
#         3 : '北师大版',
#         4 : '苏教版',
#         5 : '浙教版',
#         46: '北京课改版',
#         99 : '青岛版',
#         8 : '湘教版',
#         32 : '沪教版',
#         15 : '粤教版'
# }
New_Local_Dir = '/home/admin/store_efd'

del_scripts = "<script type='text/javascript' defer='defer'>function GetPhoneCat() {var userAgentInfo = navigator.userAgent;var Agents = new Array(\"Android\", \"iPhone\", \"SymbianOS\", \"Windows Phone\", \"iPad\", \"iPod\");var platname = \"Android\";var isPC = true;for (var v = 0; v<Agents.length; v++) {if (userAgentInfo.indexOf(Agents[v]) > 0) { platname = Agents[v]; isPC = false;break;}}return platname;}function GetKnowledgeAnalysis(knowledgeid,knowledgename) {var phoneCat = GetPhoneCat();if (phoneCat === \"Android\") {window.testSite.toTestSite(knowledgeid,knowledgename);}if (phoneCat === \"iPhone\"||phoneCat === \"iPad\"||phoneCat === \"iPod\") {toTestSite(knowledgeid,knowledgename);} }</script>"

def change_pic_format(old_pic_file, new_pic_file):
    # im = Image.open(old_pic_file)
    # im = im.convert('RGB')
    # im.save(new_pic_file)  # or 'test.tif'
    shutil.copy(old_pic_file, new_pic_file)
    return new_pic_file


def get_short_md5(md_str):
    m2 = hashlib.md5()
    m2.update(md_str)
    ret_str = m2.hexdigest()
    return ret_str[-24:]

def dispose_img(html_body, grade_id):
    new_html = html_body
    img_list = re.findall(r'src=\"(http://efd-pic.image.alimmdn.com[^\"]*?)\"', html_body)
    for img_url in img_list:
        url_parser = urlParser(img_url)
        file_name = os.path.basename(url_parser.getPath())
        pic_format = file_name[-4:]
        local_file_path = os.path.join(mfg_config.Store_Path, str(grade_id), file_name)
        if not os.path.exists(local_file_path):
            Log.error('file not exist:' + local_file_path)
            continue
        new_file_name = get_short_md5(file_name) + pic_format
        new_local_path = os.path.join(New_Local_Dir, str(grade_id), new_file_name)
        new_img_file = change_pic_format(local_file_path, new_local_path)
        new_url = mfg_config.Pics_Url_head + Pic_Root + '/' + str(grade_id) + '/' + new_file_name
        new_html = new_html.replace(img_url, new_url)
    return new_html

def dispose_content(book_id, grade_id):
    conn = Mysql_Pool.get_conn()
    # sql = "select * from question_bank where book_id = " + str(book_id)
    sql = "select * from question_bank where question_id > 60000000000000  and question_head = ''"
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    for q_one in cu.fetchall():
        content_js = json.loads(q_one['content'], encoding="utf-8")
        question_body_html = content_js['question_body_html']
        answer_analysis = content_js['answer_analysis']
        diff_list = re.findall(r"1213star_l.png", answer_analysis)
        difficulty = len(diff_list)

        question_body_html = dispose_img(question_body_html, grade_id)
        question_body_html = question_body_html.replace('魔方格', '')
        answer_analysis = dispose_img(answer_analysis, grade_id)
        answer_analysis = answer_analysis.replace('魔方格', '')
        answer_analysis = answer_analysis.replace(del_scripts, '')

        analysis_bt = BeautifulSoup(answer_analysis)
        q_body_bt = BeautifulSoup(question_body_html)
        #print analysis_bt.tr
        # difficulty move to end
        question_head = q_body_bt.get_text().strip()

        # get know_id from analysis
        know_ids_list = re.findall(r"onclick=GetKnowledgeAnalysis\(([^\)]*)\)", answer_analysis)
        know_analysis = {}
        subject = q_one['subject']
        for id_str in know_ids_list:
            if len(id_str) < 5:
                continue
            items = id_str.split(',')
            k_id = items[0]
            new_sub = str(subject) if subject > 9 else '9' + str(subject)
            new_grade = str(grade_id) if grade_id > 9 else '0' + str(grade_id)
            new_k_id = k_id if int(k_id) > 9999 else '0' + k_id
            e_know_id = int(new_sub + new_grade + new_k_id)
            k_name = items[1][1:-1]
            know_analysis[e_know_id] = k_name

        # change_some_variable
        know_node_list = re.findall(r"(onclick=GetKnowledgeAnalysis\([^\)]*\))", answer_analysis)
        for id_str in know_node_list:
            answer_analysis = answer_analysis.replace(id_str, ' ')

        # update question_bank
        content = {
         'question_body' : '',
         'know_analysis' : know_analysis,
         'question_body_html' : question_body_html,
         'answer_analysis' : answer_analysis
        }
        json_str = json.dumps(content, ensure_ascii=False,indent=2)

        one_question = {}
        one_question['question_id'] = q_one['question_id']
        one_question['content'] = json_str
        one_question['question_head'] = question_head
        one_question['difficulty'] = difficulty
        update_question(one_question)
    cu.close()
    return books

def update_question(one_question):
    sql = 'update question_bank set content = %s, question_head = %s, difficulty = %s where question_id = %s';
    params_con = ( one_question['content'], one_question['question_head'], one_question['difficulty'],
                   one_question['question_id'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

def get_book_ids(subject, grade_id):
    books = {}
    conn = Mysql_Pool.get_conn()
    sql = "select * from book_info where subject = " + str(subject)
    if grade_id < 10:
        sql += ' and grade_id = ' + str(grade_id)
    else :
        sql += ' and grade_id in (10, 11, 12)'
    sql += ' order by version_id asc'
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    for one in cu.fetchall():
        books[one['book_id']] = one
        Books_Info[one['book_id']] = one
        Old_To_Bookid[one['old_id'] + '_' + str(one['subject'])] = one['book_id']
    cu.close()
    return books

def get_subjects(grade_id):
    if grade_id < 3:
        return ['02', '01', '03']
    elif grade_id < 7:
        return ['02', '01', '03']
    elif grade_id < 10:
        return ['02', '09', '04', '05', '08', '07','01', '03', '07']
    elif grade_id < 13:
        return ['07', '08', '09', '02', '03', '01', '04', '05', '06']
    else :
        return []

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    Wantu_File.initial()
    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    log_file = '/tmp/clean_question_' + str(grade_id)
    Log.init_log(log_file)

    subjects = get_subjects(grade_id)
    old_grade = mfg_config.compare_check['in_grade'][grade_id]

    for old_subject in subjects:
        efd_subject = mfg_config.compare_check['subject'][old_subject]
        books = get_book_ids(efd_subject, grade_id)
        if len(books) == 0:
            continue
        for bk_id in books:
            Log.info('dispose book_id:'+ str(bk_id))
            dispose_content(bk_id, grade_id)
    Mysql_Pool.close_mysql()
