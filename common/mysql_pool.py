#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")
import mfg_config
import MySQLdb

# db_host = 'one.xiaofudao.com'
# db_port = 3306
# db_user = 'efd_user'
# db_name = 'efd_db'
# db_passwd = 'efudao@2015'

class Mysql_Pool(object) :
    _connect = None

    @staticmethod
    def connect_mysql(db_config=None) :
        if not db_config:
            db_config = mfg_config
        Mysql_Pool._connect = MySQLdb.connect(
            host = db_config.db_host,
            port = db_config.db_port,
            user = db_config.db_user,
            passwd = db_config.db_passwd,
            db = db_config.db_name,
            charset='utf8'
        )
        return Mysql_Pool._connect

    @staticmethod
    def get_conn():
        return Mysql_Pool._connect

    @staticmethod
    def close_mysql():
        Mysql_Pool._connect.close()

