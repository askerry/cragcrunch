# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/Users/amyskerry/.spyder2/.temp.py
"""
import os

rootdir='/home/amyskerry/Projects/cragcrunch/mpscraper'
filename=os.path.join(rootdir, 'log','errorlog2.txt')
with open(filename) as f:
    errorstr=f.read()
errors=errorstr.split(' (')
errorurls=list(set(['http://www.'+e[:e.index(')')] for e in errors if ')' in e]))

