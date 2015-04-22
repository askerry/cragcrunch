# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/Users/amyskerry/.spyder2/.temp.py
"""
import os
import string

following=False

rootdir='/home/amyskerry/Projects/cragcrunch/mpscraper'
filename=os.path.join(rootdir, 'log','errorlog2.txt')
with open(filename) as f:
    errorstr=f.read()
errors=errorstr.split(' (')
errorurls=list(set(['http://www.'+e[:e.index(')')] for e in errors if ')' in e]))

#urls=errorurls

with open("startingurls.txt", 'rb') as f:
    urls=f.read()
    climb_urls=urls.split(', ')
    
user_urls = [
        "http://www.mountainproject.com/community/"
    ]
for l in string.lowercase:
    user_urls.append('http://www.mountainproject.com/community/'+l)

