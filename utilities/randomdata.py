# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 13:20:36 2015

@author: amyskerry
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 20:42:58 2014

@author: amyskerry
"""

import sys
import prep
from collections import OrderedDict

grades, rawgrades, bouldergrades = ['3rd','4th', 'Easy 5th'],['3rd','4th','Easy 5th'],['V?']
for i in range(0,16):
    rawgrades.append('5.'+str(i))
    if i<10:
        suffixes=['-','','+']
    else:
        suffixes=['-','a','a/b','b','','b/c','c','c/d','d','+']
    for l in suffixes:
        grades.append('5.'+str(i)+l)
    for l in ['-','','+']:
        bouldergrades.append('V'+str(i)+l)
        

blockterms=['flake', 'flake_description', 'cracks', 'cracks_description', 'bolted','bolted_description']
askterms=['flakes', 'hand','tricky','undercling','slab','clipping','technical','boulder','bulge','bolted','steep', 'jug','chimney', 'crack','crux','roof','flake','cracks','traverse','pitch']
labeldict={'hand':'hand cracks','tricky':'tricky moves','undercling':'underclings','slab':'slabs','clipping':'delicate clips','technical':'technical moves','boulder':'bouldery moves','bulge':'bulges','steep':'steep climbs', 'jug':'juggy holds','chimney':'chimney climbs', 'crack':'crack climbs','crux':'tough cruxes','roof':'roofs','flake':"flakes",'traverse':'traverses','pitch':'multipitch climbs', 'crimp':'crimps'}



ndictgrades={c:prep.numerizegrades(c, gradelists=[grades]) for c in grades}
ndictgrades_r={item[1]:item[0] for item in ndictgrades.items()}
ndictbouldergrades={c:prep.numerizegrades(c, gradelists=[bouldergrades]) for c in bouldergrades}
ndictbouldergrades_r={item[1]:item[0] for item in ndictbouldergrades.items()}


def getbouldergrades():
    gdict={item[0]:item[1] for item in ndictbouldergrades_r.items() if '+' not in item[1] and '-' not in item[1] and '/' not in item[1] and '?' not in item[1]}
    ordered=sorted(gdict.keys())
    return OrderedDict((key, gdict[key]) for key in ordered)

def getroutegrades():
    gdict={item[0]:item[1] for item in ndictgrades_r.items() if '+' not in item[1] and '-' not in item[1] and '/' not in item[1] and 'rd' not in item[1]}
    ordered=sorted(gdict.keys())
    return OrderedDict((key, gdict[key]) for key in ordered)

listgrades_boulder=getbouldergrades()

listgrades_route=getroutegrades() 
    

routetypes=['Trad', 'Sport', 'Toprope', 'Boulder', 'Ice', 'Miaxed', 'Aid', 'Alpine']

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

