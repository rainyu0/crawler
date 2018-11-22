#!/usr/bin/env python
# -*- coding: UTF-8 -*-

######################################################################
#
# Author: Ging - jinghui.zhongjh@alibaba-inc.com
# File: runner.py
# Desc: 
#
# Log:
#     Create by Ging, 2010/08/03 03:15
#     Last modified by Ging, 2010/08/03 03:30
#
######################################################################

import sys
import subprocess

def run_cmd(cmd, to_stdout = False):
    my_stdout = ''
    my_stderr = ''
    process = subprocess.Popen(cmd,stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, close_fds=True)
    (stdoutdata, stderrdata) = process.communicate()
    if stdoutdata is not None and len(stdoutdata) > 0 :
        if to_stdout : 
            sys.stdout.write(stdoutdata)
        else:
            my_stdout = my_stdout + stdoutdata
    if stderrdata is not None and len(stderrdata) > 0 :
        if to_stdout :
            sys.stdout.write(stderrdata)
        else:
            my_stderr = my_stderr + stderrdata
    return (process.returncode,my_stdout,my_stderr)

def run(cmd):
    return run_cmd(cmd)

if __name__ == '__main__':
    cmd = 'w'
    (ret_code,my_stdout,my_stderr) = run_cmd(cmd,True)
    print 'run_cmd("%s", True)' % cmd 
    print 'ret_code = [%d]' % ret_code
    print 'my_stdout = [%s]' % my_stdout
    print 'my_stderr = [%s]' % my_stderr 
    (ret_code,my_stdout,my_stderr) = run_cmd(cmd,False)
    print 'run_cmd("%s", False)' % cmd 
    print 'ret_code = [%d]' % ret_code
    print 'my_stdout = [%s]' % my_stdout
    print 'my_stderr = [%s]' % my_stderr 

    cmd = 'ls xxxx/sde'
    (ret_code,my_stdout,my_stderr) = run_cmd(cmd,True)
    print 'run_cmd("%s", True)' % cmd 
    print 'ret_code = [%d]' % ret_code
    print 'my_stdout = [%s]' % my_stdout
    print 'my_stderr = [%s]' % my_stderr 
    (ret_code,my_stdout,my_stderr) = run_cmd(cmd,False)
    print 'run_cmd("%s", False)' % cmd 
    print 'ret_code = [%d]' % ret_code
    print 'my_stdout = [%s]' % my_stdout
    print 'my_stderr = [%s]' % my_stderr 

