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
from crawl.common.runner import run_cmd

New_Local_Dir = '/home/admin/store_efd/0'
Pic_Root = 'qb'


def get_short_md5(md_str):
    m2 = hashlib.md5()
    m2.update(md_str)
    ret_str = m2.hexdigest()
    return ret_str[-24:]

def dispose_img(html_body):
    new_html = html_body
    img_list = re.findall(r'src=\"(http://efd-pic.image.alimmdn.com[^\"]*?)\"', html_body)
    for img_url in img_list:
        url_parser = urlParser(img_url)
        file_name = os.path.basename(url_parser.getPath())
        pic_format = file_name[-4:]
        new_file_name = get_short_md5(file_name) + pic_format
        new_local_path = os.path.join(New_Local_Dir, new_file_name)
        cmd_str = "wget " + img_url + ' -O ' + new_local_path
        run_cmd(cmd_str)
        new_url = mfg_config.Pics_Url_head + Pic_Root + '/0/' + new_file_name
        new_html = new_html.replace(img_url, new_url)
    return new_html

def dispose_sql(sql, field_name, key_field, table_name):
    conn = Mysql_Pool.get_conn()
    cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cu.execute(sql, [])
    update_data = {}
    for one in cu.fetchall():
        f = one[field_name]
        new_f = dispose_img(f)
        key_value = one[key_field]
        update_data[key_value] = new_f
    cu.close()

    for kid in update_data:
        update_sql = 'update ' + table_name + ' set ' + \
                     field_name + '= %s where '  + key_field + ' = %s'
        params_con = (update_data[kid], kid)
        u_cu = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        u_cu.execute(update_sql, params_con)
        conn.commit()
        u_cu.close()


if __name__ == '__main__':
    Mysql_Pool.connect_mysql()
    Wantu_File.initial()
    grade_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    log_file = '/tmp/clean_question_' + str(grade_id)
    Log.init_log(log_file)

    # sql = 'select * from book_info'
    # dispose_sql(sql, 'pic', 'book_id', 'book_info')

    sql = "select * from know_desc "
    dispose_sql(sql, 'detail', 'id', 'know_desc')


