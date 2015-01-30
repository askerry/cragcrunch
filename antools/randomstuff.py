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
import clean
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
        
blockterms=['easy', 'hard', 'clipping', 'gear', 'easy_description','hard_description','clipping_description','gear_description','easy_commentsmerged','hard_commentsmerged','clipping_commentsmerged','gear_commentsmerged']        
labeldict={'ledge':'good belay ledges','undercling':'underclings','steep':'steep climbs','pump':'pumpy climbs','clipping':'exciting clipping','arete':'aretes','crack':'cracks','gear':'good gear placements','slab':'slabs','crimp':'crimps','traverse':'traverses','technical':'technical climbs','crux':'tough cruxes','vertical':'vertical climbs','boulder':'bouldery moves','corner':'corners'}


ndictgrades={c:clean.numerizegrades(c, gradelists=[grades]) for c in grades}
ndictgrades_r={item[1]:item[0] for item in ndictgrades.items()}
ndictbouldergrades={c:clean.numerizegrades(c, gradelists=[bouldergrades]) for c in bouldergrades}
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
holdterms=['crimp','pinch','jug','sloper','ledge','pocket','sidepull','dyno', 'deadpoint','heelhook','toehook','bat-hang', 'undercling', 'crack', 'flake', 'arete','gaston', 'layback','handcrack', 'flaringcrack','fingerscrack', 'widecrack','thincrack', 'offwidth', 'chimney','diahedral','corner', 'traverse']
descriptors=['steep','overhung','slab','technical','thin', 'ramp','sporty','vertical', 'boulder']
easeterms=['easy','hard','stiff','pump','beginner','hung','take','difficult', 'committing', 'crux', 'soft','sandbag', 'awkward','creative','comfortable']
safetyterms=['runout','spicy','exciting','nervous','sketchy','pro', 'deck', 'gear', 'protect','fall','rusty','clipping','swing', 'tenuous', 'nopro', 'mental']
rockterms=['granite', 'limestone', 'schist', 'patina','sandstone', 'conglomerate', 'quartzite', 'gneiss', 'basalt']

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

