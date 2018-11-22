# -*- coding: utf-8 -*-


CHARSET = 'UTF-8'
SDK_VERSION = '1.0.0'
MANAGE_API_VERSION = '3.0'

UPLOAD_ENDPOINT = 'http://upload.media.aliyun.com'
MANAGE_ENDPOINT = 'http://rs.media.aliyun.com'

UPLOAD_API_UPLOAD = '/api/proxy/upload.json'
UPLOAD_API_BLOCK_INIT = '/api/proxy/blockInit.json'
UPLOAD_API_BLOCK_UPLOAD = '/api/proxy/blockUpload.json'
UPLOAD_API_BLOCK_COMPLETE = '/api/proxy/blockComplete.json'
UPLOAD_API_BLOCK_CANCEL = '/api/proxy/blockCancel.json'

TYPE_TOP = 'TOP'
TYPE_CLOUD = 'CLOUD'

UPLOAD_USER_AGENT = 'ALIMEDIASDK_PYTHON_'

DETECT_MIME = 1
DETECT_MIME_NONE = 0
INSERT_ONLY = 1
INSERT_ONLY_NONE = 0
MIN_OBJ_SIZE = 102400 #1024*100
SUB_OBJ_SIZE = 10485760 #1024*1024*10