#!/usr/bin/env python
# -*- coding: utf-8 -*-

from want import Want, utils
import time
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

Pics_Root_Path = 'qb'

class Wantu_File:
    _wantu_client = None
    _msconds = int(time.time() * 1000) + 3600 * 6000
    _ps = {'detectMime': 1, 'expiration': int(time.time() * 1000) + 3600 * 1000, 'insertOnly': 0,
          'namespace': 'efd-p', 'sizeLimit': 0}

    @staticmethod
    def initial():
        Wantu_File._wantu_client = Want('23255887', '467120e5a644b4df94192990306f232c')

    @staticmethod
    def upload_file(file_path, pic_root=Pics_Root_Path):
        file_name = os.path.basename(file_path)
        result = Wantu_File._wantu_client.upload_file(Wantu_File._ps, pic_root, file_name, file_path)
        return result['url']

if __name__ == '__main__':
    Wantu_File.initial()
    root_path = '/home/admin/store_efd'
    dir_list = os.listdir(root_path)
    for s_dir in dir_list:
        file_list = os.listdir(os.path.join(root_path, s_dir))
        print s_dir + ' has ' + str(len(file_list))
        for file in file_list:
            f_path = os.path.join(root_path, s_dir, file)
            try:
                url = Wantu_File.upload_file(f_path, 'qb/' + s_dir)
            except:
                print 'Error! url:', url