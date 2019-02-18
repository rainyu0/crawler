#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd
import json

from parseHolland import excelParser

Explain_Json_Schema = {u'代码': 'code', u'适合的典型专业':'holland_spec', u'适合的典型职业':'holland_career', u'对应学信网专业百科':'xuexin_spec' }
Xuexin_Json_Schema = {u'专业名称':'speciality_name', u'门类':'class', u'学科':'subject', u'一级行业':'industry' }

#ShortName_Chinese = {'code' : u'代码', 'holland_spec': u'适合的典型专业', 'holland_career':u'适合的典型职业', 'xuexin_spec':u'对应学信网专业百科' }
Field_Order = [u'代码', u'适合的典型专业', u'对应学信网专业百科', u'一级行业']

def find_max_industry(industry_count):
    max_value = 0
    max_type = ''
    for industry in industry_count:
        if industry_count[industry] > max_value:
            max_value = industry_count[industry]
            max_type = industry
    return max_type

def write_json_file(data_list, out_file):
    fdout = open(out_file, 'w')
    for line in data_list:
        json_str = json.dumps(line, ensure_ascii=False, indent=2)
        json_str = json_str.encode('utf-8')
        fdout.write(json_str)
        fdout.write('\n')
    fdout.close()

def write_csv_file(data_list, out_file):
    fdout = open(out_file, 'w')
    #first write table head
    for chinese in Field_Order:
        fdout.write(chinese.encode('utf-8') + ',')
    fdout.write('\n')

    for line in data_list:
        #TODO:
        for field in Field_Order:
            if field == u'一级行业':
                vl = line['industry']
            else:
                short = Explain_Json_Schema[field]
                vl = line[short]
            vl = vl.replace(",", ";", 9999);
            fdout.write(vl.encode('utf-8') + ',')
        fdout.write('\n')
    fdout.close()

if __name__ == '__main__':
    explain_data_list = excelParser.excel_table_byindex('1.HLD代码职业行业对应表.xlsx', Explain_Json_Schema)
    xuexin_data_list = excelParser.excel_table_byindex('3.学信网专业行业匹配表20190214.xls', Xuexin_Json_Schema)

    #学信网专业 =》 一级行业的dict
    spec_industry_dict = {}
    for one in xuexin_data_list:
        spec_industry_dict[one['speciality_name']] = one['industry']

    for one_explain in explain_data_list:
        specs = one_explain['xuexin_spec'].split(',')
        specs_length = len(specs)
        industry_count = {}
        for one_spec in specs:
            if one_spec in spec_industry_dict:
                industry = spec_industry_dict[one_spec]
                if industry in industry_count:
                    industry_count[industry] += 1
                else:
                    industry_count[industry] = 1
                if industry_count[industry] >= specs_length/2:
                    one_explain['industry'] = industry
        #如果没有industry字段，找出最大的。
        if not one_explain.has_key('industry'):
            industry = find_max_industry(industry_count)
            one_explain['industry'] = industry


    # 写入结果文件JSON
    write_json_file(explain_data_list, 'new_Holland_explain.json')
    write_csv_file(explain_data_list, 'new_Holland_explain.csv')




