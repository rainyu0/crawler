#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd
import json


Holland_Field_Reflex = {u"编号":"question_id", u"题目":"question_body", u"答案":"question_options",
                        u"权重":"weight", u"类型":"class_desc",
                        u"英文字母":"class_letter", u"描述":"description", u"具体表现":"detail_display"}
MBTI_Field_Reflex = {u"序号": "question_id", u"选项":"question_options", u"权重":"weight", u"引导语":"question_lead",
                     u"题目": "question_body"}

MBTI_Explain_Field_Reflex = {u"维度":"dim", u"类型":"class_desc", u"描述":"description", u"行事风格":"behavior_style"}

Competence_Field_Reflex = {u"题号":"question_id", u"能力类型":"Competence_type",u"答案":"question_options",
                           u"权重":"weight", u"题目":"question_body" }

def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)

def excel_table_byindex(file, fields_dict= {} ,colnameindex=0,by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows #行数
    colnames =  table.row_values(colnameindex) #某一行数据
    list =[]
    for rownum in range(1,nrows):
         row = table.row_values(rownum)
         if row:
             app = {}
             for i in range(len(colnames)):
                 #转化列名
                 old_column = colnames[i]
                 if old_column in fields_dict :
                     colName = fields_dict[old_column]
                     colValue = row[i]
                     app[colName] = colValue
                     if isinstance(colValue, float) :
                         app[colName] = int(colValue)
                 else :
                     print "ERROR! Not in Dict field:" + colnames[i]
             list.append(app)
    return list


def dispose_question_file(input_file,  output_file, fields_dict):
    data_list = excel_table_byindex(input_file, fields_dict)
    fdout = open(output_file, 'w')
    for line in data_list:
        json_str = json.dumps(line, ensure_ascii=False, indent=2)
        json_str = json_str.encode('utf-8')
        fdout.write(json_str)
        fdout.write('\n')
    fdout.close()



if __name__ == '__main__':
    dispose_question_file("职业兴趣类型测试.xlsx", "holland_question.json", Holland_Field_Reflex)
    dispose_question_file("MBTI题目.xlsx", "MBTI_question.json", MBTI_Field_Reflex)
    dispose_question_file("MBTI维度解析改.xlsx", "MBTI_explain.json", MBTI_Explain_Field_Reflex)
    dispose_question_file("职业能力倾向测试.xlsx", "competence_question.json", Competence_Field_Reflex)
    print "excel parse ok!"