# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] == 3:
    import http.client as httplib
    def b(str):
        return str.encode('utf-8')
else:
    def b(str):
        return str

try:
    import simplejson as json
except Exception:
    import json