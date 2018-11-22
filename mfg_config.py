#!/usr/bin/env python
# -*- coding: utf-8 -*-

Host = 'mfg.mofangge.com'
Pic_Host = 'pic2.mofangge.com'
Port = 80
Store_Path = '/home/admin/store/gfm'
Pics_Url_head = 'http://efd-p.image.alimmdn.com/'

Book_List_Path = 'http://mfg.mofangge.com:80/MfgArea/UserBasicInfo/GetAllBookList?subject=02&grade=c1&edution=0&science=2'
# Book_List_Path = 'http://mfg.mofangge.com:80/MfgArea/UserBasicInfo/GetAllBookList?'
Text_Book_Chapter = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetTextbookChapter?grade=x5&subject=02&bookId=001x50&term=0&science=2&edution=0'
Book_Chapter = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetChapters?subject=02&grade=x5&bookid=001x51&term=1'
Knowledge_Path = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetKnowledgePointList?subject=02&chapterid=001c1002&grade=c1'
question_dettail_path = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetQuestionDetail?grade=c1&sub=02&knowId=249'
# question_id,A,3|'''
question_answer_path = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetUserExerciseSingleResult?' \
                       'chapterId=001c1001&knowid=247&questionResult=684319%2CA%2C3%7C678226%2CA%2C1%7C1122194%2CB%2C1%7C670245%2CC%2C1%7C741987%2CD%2C1&useTime=12&grade=c1&subjectId=02&phoneType=9'
answer_analysis_path = 'http://mfg.mofangge.com:80/MfgArea/UserExercise/GetQuestionAnalysis?sub=02&topicId=684319'

knowledge_analysis_path = 'http://mfg.mofangge.com:80/MfgArea/UserEvaluation/KnowledgeAnalysis?subject=01&grade=c1&pointId=124'
# result[pointInfo]
Modify_Book = 'http://mfg.mofangge.com:80/MfgArea/UserBasicInfo/ModifyBook?bookIdStr=001x30%2C001x31%2C001x40%2C001x41%2C001x50%2C001x51%2C001x60%2C001x61&subject=03&bookVersion=%E4%BA%BA%E6%95%99%E7%89%88&grade=x5'

grade_config = {'小升中' : '21', '中考' : '22', '高考' : '23', '必修': '30', '选修' : '50' }
u_wl = {'理科': '0', '文科' : '1', '文理不分' : '2'}

compare_check = {
    'grade' : {'x1' : 1, 'x2' : 2, 'x3' : 3, 'x4' : 4, 'x5' : 5, 'x6' : 6,
               'c1' : 7, 'c2' : 8, 'c3' : 9,
               'g1' : 10, 'g2' : 11, 'g3' : 12, 'g': 10 },
    'in_grade' : {1 : 'x1', 2 : 'x2', 3 : 'x3', 4 : 'x4', 5 : 'x5', 6 : 'x6',
               7 : 'c1', 8 : 'c2', 9 : 'c3',
               10 : 'g1', 11 : 'g2', 12 : 'g3'},
    'book' : {'001c10' : 92071, '001c11' : 92072, '001c20' : 92081, '001c21' : 92082, '001c30' : 92091, '001c31' : 92092 },
    'subject' : {'02' : 1, '01' : 2, '03' : 3, '04' : 7, '05': 8, '06':6, '07':5, '08': 4, '09': 9},
    'in_subject' : {1 : '02', 2 : '01', 3 : '03', 7 : '04', 8 : '05', 6 : '06', 5 : '07', 4 : '08', 9 : '09'}
}

db_host = 'one.xiaofudao.com'
db_port = 3306
db_user = 'efd_user'
db_name = 'efd_db'
db_passwd = 'efudao@2015'

Min_Question_Id = 60 * 10 * 10 * 10000 * 10000000

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

# Url_Header = getUrlHeader('header')











