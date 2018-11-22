#!/usr/bin/env python
# -*- coding: UTF-8 -*-

######################################################################
#
# Author: Ging - jinghui.zhongjh@alibaba-inc.com
# File: log.py
# Desc:
#
# Log:
#     Create by Ging, 2010/08/19 19:42
#     Last modified by Ging, 2010/08/19 19:42
#
######################################################################

import os
import logging
import logging.handlers

class Log(object) :
    __logger = None
    
    @staticmethod
    def init_log(log_path = '',force=False) :
        if Log.__logger is not None and not force:
            return

        if len(log_path) == 0:
            logging.basicConfig(level=logging.WARNING)
            logger = logging.getLogger()
        else:
            log_dir = os.path.dirname(log_path)
            log_name = os.path.basename(log_path)
            if not os.path.exists(log_dir) :
                os.makedirs(log_dir)
            logger = logging.getLogger(log_name)


            if not log_path.endswith('.log'):
                log_path += '.log'

            hdlr = logging.handlers.RotatingFileHandler(log_path, maxBytes=80*1024*1024, backupCount=3)
            formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)
        Log.__logger = logger

        for attrname in ('setLevel','debug','info','warn','error','fatal','critical') :
            func = getattr(Log.__logger,attrname,None)
            if func is not None and callable(func) :
                setattr(Log, attrname, func)

if __name__ == '__main__' :
    import sys
    if len(sys.argv) > 1 :
       Log.init_log(sys.argv[1])
    else:
        Log.init_log()
    Log.setLevel(logging.DEBUG)
    Log.debug('debug')
    Log.info('info')
    Log.warn('warn')
    Log.error('error')
    Log.fatal('fatal')
    Log.critical('critical')

