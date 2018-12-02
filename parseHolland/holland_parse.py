#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import json
import config
from common.mysql_pool import Mysql_Pool

Question_Tag = '霍兰德职业兴趣测验'

def insert_question(one_question):
    one_question["content"] = ""
    sql = "insert into question_bank(question_id, question_tag, gmt_modified, " \
          "evaluation_type, question_head, question_body, " \
          "question_options, grade_type,"," evaluation_attr, " \
                                          "order_no) " \
          "values(%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
          " on duplicate key update order_no = %s, question_head = %s, question_body = %s"
    params_con = (one_question["question_id"], one_question["question_tag"], "now()",
               one_question["evaluation_type"], one_question["question_head"], one_question["question_body"],
               one_question["question_options"], one_question["grade_type"],one_question["evaluation_attr"],
               one_question["order_no"],
               one_question["order_no"], one_question["question_head"], one_question["question_body"]
           )
    cu = Mysql_Pool.get_conn().cursor()
    cu.execute(sql, params_con)
    Mysql_Pool.get_conn().commit()
    cu.close()

#R实物型(与物打交道)1-10；61-70
#A艺术型(创造性思想和情感的表达):11-20；71-80
#I探究型(思考和解决问题，以得出结论或概念):21-30；81-90
#S社会型(理解他人需要并提供帮助):31-40； 91-100
#E经营型/进取型(影响和控制他人):41-50；101-110
#C事务型(与信息、规则打交道):51-60；111-120
def get_evaluation_type(order_no):
    order_int = int(order_no)
    ret = ''
    if (order_int >= 1 and order_int) <= 10 or (order_int >= 61 and order_int <= 70):
        ret = 'R'
    elif (order_int >= 11 and order_int) <= 20 or (order_int >= 71 and order_int <= 80):
        ret = 'A'
    elif (order_int >= 21 and order_int) <= 30 or (order_int >= 81 and order_int <= 90):
        ret = 'I'
    elif (order_int >= 31 and order_int) <= 40 or (order_int >= 91 and order_int <= 100):
        ret = 'S'
    elif (order_int >= 41 and order_int) <= 50 or (order_int >= 101 and order_int <= 110):
        ret = 'E'
    elif (order_int >= 51 and order_int) <= 60 or (order_int >= 111 and order_int <= 120):
        ret = 'C'
    return ret

def writeDict(question):
    return

def dispose_question_file(file_str, question_head):
    fd = open(file_str, 'r')
    fdout = open("question_out.txt", 'a+')
    file_lines = fd.readlines()
    for line in file_lines:
        arr = line.split('.')
        if len(arr) == 1 :
            continue
        order_no = arr[0]
        qid = config.question_id + 1
        config.question_id += 1
        one_question = {'question_id' : qid, 'question_tag' : Question_Tag, 'question_head' : question_head}
        one_question['question_body'] = line
        one_question['evaluation_type'] = 1
        one_question['question_options'] = 'A,B'
        one_question['grade_type'] = 1
        one_question['evaluation_attr'] = get_evaluation_type(order_no)
        one_question['order_no'] = order_no
        #insert_question(one_question)
        json_str = json.dumps(one_question, ensure_ascii=False, indent=2)
        fdout.write(json_str)
        fdout.write('\n')

    fd.close()
    fdout.close()

def dispose_output_file(file_str):
    fd = open(file_str, 'r')
    fdout = open("out.txt", 'w')
    file_lines = fd.readlines()
    desc = ''
    code = ''
    for line in file_lines:
        if line.strip().isalpha():
            code = line.strip()
        elif len(line) > 1:
            desc += line
        else:
            #id = ord(code[0]) + ord(code[1]) + ord(code[2])
            oneOut = {'answer_code': code, 'answer_desc': desc, 'evaluation_type': 1}
            json_str = json.dumps(oneOut, ensure_ascii=False, indent=2)
            fdout.write(json_str)
            fdout.write('\n')
            code = ''
            desc = ''

    fd.close()
    fdout.close()

if __name__ == '__main__':
    Mysql_Pool.connect_mysql(config)
    # dispose_question_file('first.txt','您愿意从事下列活动吗？')
    # dispose_question_file('second.txt','您具有擅长或胜任下列活动的能力吗？')
    dispose_output_file('output.txt')





