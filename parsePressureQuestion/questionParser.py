#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

Holland_Field_Reflex = {u"编号":"question_id", u"题目":"question_body", u"答案":"question_options",
                        u"权重":"weight", u"类型":"class_desc",
                        u"英文字母":"class_letter", u"描述":"description", u"具体表现":"detail_display"}

def dispose_question_file(src_file, output_file, table_scheme):
    file = open(src_file, 'r')
    fdout = open(output_file, 'w')
    lines = file.readlines()
    id_class_dict = {}
    for line in lines:
        if line.find('：') != -1:
            items = line.split('：')
            class_desc = items[0]
            q_ids = items[1].split('、')
            for qid in q_ids:
                id_class_dict[qid.strip()] = class_desc
        if line.find('（') != -1:
            one = {}
            front_index = line.find('（')
            back_index = line.find('）') if line.find('）') != -1  else line.find(')')
            qid = line[front_index + len('（') : back_index].strip()
            one['question_id'] = qid
            one['question_body'] = line.strip()
            one['class_desc'] = id_class_dict[qid]
            one['question_options'] = '1、是； 2、否'
            json_str = json.dumps(one, ensure_ascii=False, indent=2)
            #json_str = json_str.encode('utf-8')
            fdout.write(json_str)
            fdout.write('\n')
    file.close()
    fdout.close()



if __name__ == '__main__':
    dispose_question_file("pureQuestion.txt", "pressure.json", Holland_Field_Reflex)