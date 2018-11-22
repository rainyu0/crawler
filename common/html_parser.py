#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from sgmllib import SGMLParser

class ListName(SGMLParser):
	def __init__(self):
		SGMLParser.__init__(self)
		self.is_img = ""
		self.name = []
	def start_img(self, attrs):
		self.is_img = 1
	def end_img(self):
		self.is_img = ""
	def handle_data(self, text):
		if self.is_img == 1:
			self.name.append(text)

content = "<table><tbody><tr><td><div>如图所示的三视图表示的几何体是<br><img src=\"http://pic2.mofangge.com/upload/papers//20140823/201408230029499861099.png\" style=\"vertical-align:middle;\"><table name=\"optionsTable\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\"><tr><td>A．长方体 </td></tr><tr><td>B．正方体</td></tr><tr><td>C．圆柱体</td></tr><tr><td>D．三棱柱</td></tr></table></div></td></tr></tbody></table><script type='text/javascript' defer='defer'>window.addEventListener('load',function(){var imgArr =document.getElementsByTagName('img');if(imgArr.length >= 1){for(var i= 0;i < imgArr.length ;i++){var img = imgArr[i];var w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;if(w<=0 || w=='NaN'){w=305;};if(img.width > w){img.setAttribute('width','100%');}img.setAttribute('max-width','100%');}} var tableArr = document.getElementsByTagName('TABLE');if(tableArr.length > 0){var tb = tableArr[0];               var text = tb.style.cssText + ' line-height:150%;-webkit-text-size-adjust:none;';tb.setAttribute('style',text);}    }) </script>"
listname = ListName()
listname.feed(content)
for item in listname.name:
	print item
