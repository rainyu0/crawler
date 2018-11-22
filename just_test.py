#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #!/usr/bin/python
# # -*- coding: utf-8 -*-
#
# from bs4 import BeautifulSoup
#
# html_doc = """
# <html><head><title>The Dormouse's story</title></head>
# <body>
# <p class="title"><b>The Dormouse's story</b></p>
#
# <p class="story">Once upon a time there were three little sisters; and their names were
# <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
# <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
# <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
# and they lived at the bottom of a well.</p>
#
# <p class="story">...</p>
#
# """
#
# soup = BeautifulSoup(html_doc)
#
# print soup.title
#
# print soup.title.name
#
# print soup.title.string
#
# print soup.p
#
# print soup.a
#
# print soup.find_all('a')
#
# print soup.find(id='link3')
#
# print soup.get_text()
#
# ls = ['1', '3', '4']
# print ','.join(ls)
#
# from PIL import Image
# im = Image.open('/Users/shengyu/store/gfm/12132015083114420227617610.png')
# im = im.convert('RGB')
# im.save('/Users/shengyu/Downloads/ii.jpg')  # or 'test.tif'
#
# import hashlib
#
# m2 = hashlib.md5()
# m2.update('aaa')
# print m2.hexdigest()
#
# import json
#
# know_analysis = {'df' : 'df', 'ee' : '9'}
# content = {
#          'question_body' : '',
#          'know_analysis' : know_analysis,
#          'question_body_html' : '343',
#          'answer_analysis' : 'dfd'
#         }
# json_str = json.dumps(content, ensure_ascii=False,indent=2)
# print json_str
#
# s='kkdf;dfd   '
# d = s.strip()
# print d
# print len(d)
#
# print s.replace('df', '')

s = '[p]若正比例函数[tex=2.929x1.286]v24vrbOGix+dpCbY/14Hrg==[/tex]的图象经过点[tex=2.143x1.286]3aRQnhkuQlVmA13kcfRDjQ==[/tex]，' \
    '则[tex=0.571x1.286]pc/qlnA3cxu8Ag9jp3tYHQ==[/tex]的值为（  ）。[/p]'

import re
img_list = re.findall(r'\[tex=[^\]]*\]([^\[]*)', s)
for img_url in img_list:
    print img_url
