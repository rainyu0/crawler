#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time

dd = {'234': 'dd', '4' : 'kk'}
for k in dd:
    print k

# print unicode(code_str)
# print code_str.decode("unicode-escape")
# #utf8_str = code_str.decode('utf8')
# #print utf8_str
#
# a = bytes('\u003ctable\u003e你好')
# print len(a)
# print a.decode("unicode-escape")
# print unicode(a)


img_src = "<table><tbody><tr><td><div>\u5982\u56fe\u6240\u793a\u7684\u4e09\u89c6\u56fe\u8868\u793a\u7684\u51e0\u4f55\u4f53\u662f<br><img src=\"http://pic1.mofangge.com/upload/papers//20140823/201408230029499861099.png\" style=\"vertical-align:middle;\"><table name=\"optionsTable\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\"><tr><td>img style=\"height:1em\" src=\"http://pic2.mofangge.com/img/photo/star_h.png\"A\uff0e\u957f\u65b9\u4f53 </td></tr><tr><td>B\uff0e\u6b63\u65b9\u4f53</td></tr><tr><td>C\uff0e\u5706\u67f1\u4f53</td></tr><tr><td>D\uff0e\u4e09\u68f1\u67f1</td></tr></table></div></td></tr></tbody></table><script type='text/javascript' defer='defer'>window.addEventListener('load',function(){var imgArr =document.getElementsByTagName('img');if(imgArr.length >= 1){for(var i= 0;i < imgArr.length ;i++){var img = imgArr[i];var w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;if(w<=0 || w=='NaN'){w=305;};if(img.width > w){img.setAttribute('width','100%');}img.setAttribute('max-width','100%');}} var tableArr = document.getElementsByTagName('TABLE');if(tableArr.length > 0){var tb = tableArr[0];               var text = tb.style.cssText + ' line-height:150%;-webkit-text-size-adjust:none;';tb.setAttribute('style',text);}    }) </script>"
img_list = re.findall(r'src=\"(http://pic\d+.mofangge.com[^\"]*?)\"', img_src)
print img_list


data = time.strftime('%Y%m%d')
print data[0:4]



