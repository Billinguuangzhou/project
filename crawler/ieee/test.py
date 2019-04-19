#!/usr/bin/env python
# coding=utf-8

from bs4 import BeautifulSoup
import json
import re

str = u'''
<html>
    <a _ulg> aa</a>
</html>
'''

soup = BeautifulSoup(str, 'lxml')
print soup.find('a', attrs={'_ulg':''})

str = '"search":"[ALL]"'
print str
matchObj = re.search(r'\"ALL\"', str, re.M|re.I)
if matchObj:
    print 'yes'
else:
    print 'None'

json_str = re.sub(r':"\[ALL\]"', ':["ALL"]', str)
print json_str

json_str = '{"name": "billdai", "info": [["school", "scut"], "in", "kk"]}'
json_str = json.loads(json_str)
for item in json_str["info"]:
    print item
print json_str

h = '''
<td>some text</td>
<td></td>
<td><p>more text</p></td>
<td>even <p><!-- doc1 -->more text
<!-- dco --> aiqing</p></td>
'''
print h
soup = BeautifulSoup(h, 'lxml')
tds = soup.find_all(name='td')
for td in tds:
    print td.string
    print re.sub('[\r\n\t]', '', td.text)

with open('../../data/ieee/Using_Support_Vector_Machines_to_Classify_Student_Attentiveness_for_the_Development_of_Personalized_Learning_Systems.html') as f:
    data = f.read()
    soup = BeautifulSoup(data, 'lxml')
    p = soup.find_all(name='p')
    for item in p:
        print item
