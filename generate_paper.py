#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import MySQLdb
import json
import random

import mfg_config
from crawl.common.mysql_pool import Mysql_Pool
from crawl.common.tree_manager import Tree_Manager
from crawl.common.log import Log

Know_Tree = Tree_Manager()
Books_Info = {}
Old_To_Bookid = {}
Validate_Versions =  {
        0 : '',
        1 : '人教版',
        19 : '教科版',
        2 : '冀教版',
        3 : '北师大版',
        4 : '苏教版',
        5 : '浙教版',
        # 46: '北京课改版',
        # 99 : '青岛版',
        # 8 : '湘教版',
        # 32 : '沪教版',
        # 15 : '粤教版'
}

Max_Paper_Num = 10
Max_Chappter_Paper_Num = 10
Question_Num_Per_Paper = 5
Used_Questions = {}
KnowId_Had_Questions = {}

def initial_knowledge():
    conn = Mysql_Pool.get_conn()
    sql = 'select * from bak_know order by level asc'
    #first main book dispose
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    for one in know_cursor.fetchall():
        if Know_Tree.is_main_id( one['id']):
            Know_Tree.add_node(one['parent_id'], one['id'], one['name'], one['level'], one['old_id'])
    know_cursor.close()
    #second other books
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    for one in know_cursor.fetchall():
        if not Know_Tree.is_main_id( one['id']):
            Know_Tree.add_node(one['parent_id'], one['id'], one['name'], one['level'], one['old_id'])
    know_cursor.close()

# increment create paper need to del repeat question_id
def get_used_questions(book_id):
    main_book_id = int(Know_Tree.change_main_bookid(book_id))
    if main_book_id in Used_Questions:
        return Used_Questions[main_book_id]

    all_nodes = Know_Tree.get_all_nodes(main_book_id)
    if not Know_Tree.is_main_id(book_id) :
        other_nodes = Know_Tree.get_all_nodes(book_id)
        for kid in other_nodes:
            all_nodes[kid] = 1
    know_ids = []
    for k_id in all_nodes:
        know_ids.append(str(k_id))
    if len(know_ids) == 0:
        Used_Questions[main_book_id] = {}
        return {}
    conn = Mysql_Pool.get_conn()
    ids_str = ','.join(know_ids)
    sql = 'select questions, knowledge_id from tmp_paper where knowledge_id in (' + ids_str + ')'
    #first main book dispose
    know_cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    know_cursor.execute(sql, [])
    tmp_questions = {}
    for one in know_cursor.fetchall():
        q_js = json.loads(one['questions'], encoding="utf-8")
        for qid in q_js:
            tmp_questions[qid] = 1
        know_id = one['knowledge_id']
        KnowId_Had_Questions[know_id] = 1
    Used_Questions[main_book_id] = tmp_questions
    return tmp_questions

def dispose_all_knows(book_id, left_questions, all_questions, grade_id):
    # every know_id
    main_book_id = int(Know_Tree.change_main_bookid(book_id))
    for o_id in left_questions:
        old_questions = left_questions[o_id]
        random.shuffle(old_questions)
        question_num_inall = len(all_questions[o_id])
        main_know_id = Know_Tree.get_main_id(book_id, o_id)
        if not main_know_id :
            Log.error('no found ' + str(book_id) + '_' + str(o_id))
            continue
        if main_know_id in KnowId_Had_Questions:
            Log.info('Had already questions'  + str(book_id) + '_' + str(o_id))
            continue
        update_know_tree(main_know_id, question_num_inall)
        lefd_question_num = len(left_questions[o_id])
        paper_num = lefd_question_num / Question_Num_Per_Paper
        true_paper_num = paper_num if paper_num < Max_Paper_Num else Max_Paper_Num
        for i in range(0, true_paper_num):
            questions = {}
            for j in range(0, Question_Num_Per_Paper):
                index = i * Question_Num_Per_Paper + j
                q_id = old_questions[index]['question_id']
                questions[q_id] = {'order_no' : j, 'answer' : old_questions[index]['question_answer']}
                q_id_str = str(q_id)
                Used_Questions[main_book_id][q_id_str] = 1
            one_dict = {}
            one_dict['question_num'] = Question_Num_Per_Paper
            one_dict['questions'] = json.dumps(questions, ensure_ascii=False,indent=2)
            one_dict['knowledge_id'] = main_know_id
            one_dict['type'] = 1
            one_dict['status'] = 1
            one_dict['difficulty'] = 3
            one_dict['grade_id'] = grade_id
            insert_one_paper(one_dict)
        KnowId_Had_Questions[main_know_id] = 1


def dispose_all_chapters(book_id, all_questions, grade_id):
    # for every chaper paper
    chapter_questions = Know_Tree.get_nodes_by_level(book_id, 1)
    for chapter_id in chapter_questions:
        know_ids = Know_Tree.get_child_knows(book_id, chapter_id)
        chapter_questions[chapter_id] = []
        for k_id in know_ids:
            old_id = int(Know_Tree.get_old_id(k_id))
            if old_id in all_questions:
                old_list = all_questions[old_id]
                for q_one in old_list:
                    chapter_questions[chapter_id].append(q_one)

    for chapter_id in chapter_questions:
        old_questions = chapter_questions[chapter_id]
        random.shuffle(old_questions)
        question_num = len(old_questions)
        update_know_tree(chapter_id, question_num)
        paper_num = question_num / Question_Num_Per_Paper
        true_paper_num = paper_num if paper_num < Max_Chappter_Paper_Num else Max_Chappter_Paper_Num
        for i in range(0, true_paper_num):
            questions = {}
            for j in range(0, Question_Num_Per_Paper):
                index = i * Question_Num_Per_Paper + j
                q_id = old_questions[index]['question_id']
                questions[q_id] = {'order_no' : j, 'answer' : old_questions[index]['question_answer']}
            one_dict = {}
            one_dict['question_num'] = Question_Num_Per_Paper
            one_dict['questions'] = json.dumps(questions, ensure_ascii=False,indent=2)
            one_dict['knowledge_id'] = chapter_id
            one_dict['type'] = 1
            one_dict['status'] = 1
            one_dict['difficulty'] = 3
            one_dict['grade_id'] = grade_id
            insert_one_paper(one_dict)
        KnowId_Had_Questions[chapter_id] = 1

def generate_paper(book_id, e_subject, grade_id):
    used_questions = get_used_questions(book_id)
    is_main_book = Know_Tree.is_main_id(book_id)
    book_str = str(book_id)
    if not is_main_book:
        book_str += ',' + Know_Tree.change_main_bookid(book_id)

    conn = Mysql_Pool.get_conn()
    sql = "select question_id, question_answer, old_id, subject from question_bank where book_id in (" + book_str + ") and subject = " + str(e_subject) + \
                                                                        " order by old_id asc "
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    left_questions = {}
    all_questions = {}
    # book_olds = Know_Tree.get_all_old_ids(book_id)
    for q_one in cu.fetchall():
        old_id = q_one['old_id']
        sub = q_one['subject']
        if e_subject != sub:
            continue
        if old_id not in left_questions:
            left_questions[old_id] = []
            all_questions[old_id] = []
        all_questions[old_id].append(q_one)
        q_id = str(q_one['question_id'])
        if q_id not in used_questions:
            left_questions[old_id].append(q_one)
    cu.close()
    dispose_all_knows(book_id, left_questions, all_questions, grade_id)
    dispose_all_chapters(book_id, all_questions, grade_id)

def insert_one_paper(paper_dict):
    sql = 'insert into tmp_paper(question_num, knowledge_id, status, difficulty, questions, type, grade_id) ' \
          'values(%s, %s, %s, %s, %s, %s, %s) '
    params_con = (paper_dict['question_num'], paper_dict['knowledge_id'], paper_dict['status'],
                  paper_dict['difficulty'], paper_dict['questions'], paper_dict['type'], paper_dict['grade_id'])
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

def update_know_tree(know_id, q_num):
    sql = 'update bak_know set question_num = ' + str(q_num)  + ' where id = ' + str(know_id)
    Log.info('update know tree:' + sql)
    params_con = ()
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

def get_book_ids(subject, grade_id):
    books = []
    conn = Mysql_Pool.get_conn()
    sql = "select * from book_info where subject = " + str(subject)
    if grade_id < 10:
        sql += ' and grade_id = ' + str(grade_id)
    else :
        sql += ' and grade_id in (10, 11, 12)'
    sql += ' order by version_id asc '
    Log.info('get books sql:' + sql)
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    for one in cu.fetchall():
        books.append(one['book_id'])
        Books_Info[one['book_id']] = one
        Old_To_Bookid[one['old_id'] + '_' + str(one['subject'])] = one['book_id']
    cu.close()
    return books

def get_subjects(grade_id):
    if grade_id < 3:
        return ['03', '01', '02']
    elif grade_id < 7:
        return ['02', '01', '03']
    elif grade_id < 10:
        return ['07', '08', '09', '02', '03', '01', '04', '05', '06']
    elif grade_id < 13:
        return ['07', '08', '09', '02', '03', '01', '04', '05', '06']
    else :
        return []

#grade=c1&sub=02
if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    log_file = '/tmp/generate.log_normal_' + str(grade_id)
    Log.init_log(log_file)

    subjects = get_subjects(grade_id)
    old_grade = mfg_config.compare_check['in_grade'][grade_id]

    initial_knowledge()
    for old_subject in subjects:
        efd_subject = mfg_config.compare_check['subject'][old_subject]
        books = get_book_ids(efd_subject, grade_id)
        Log.info('books is:' + str(books))
        if len(books) == 0:
            continue
        for bk_id in books:
            version_id = Books_Info[bk_id]['version_id']
            if version_id not in Validate_Versions:
                continue
            Log.info('book_id:' + str(bk_id) + '==>' + str(Know_Tree.get_all_old_ids(bk_id)))
            generate_paper(bk_id, efd_subject, grade_id)
    Mysql_Pool.close_mysql()


