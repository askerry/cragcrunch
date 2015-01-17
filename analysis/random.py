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

routetypes=['Trad', 'Sport', 'Toprope', 'Boulder', 'Ice', 'Miaxed', 'Aid', 'Alpine']
holdterms=['crimp','pinch','jug','sloper','ledge','pocket','sidepull','dyno', 'deadpoint','heelhook','toehook','bat-hang', 'undercling', 'crack', 'flake', 'arete','gaston', 'layback','hand crack', 'flaring crack','fingers crack', 'wide crack','thin crack', 'offwidth', 'chimney','diahedral','corner', 'traverse']
descriptors=['steep','overhang','slab','technical','thin', 'ramp', 'overhung','sporty','vertical', 'boulder', 'bouldery']
easeterms=['easy','hard','stiff','pumpy','beginner','hang','hung','take','difficult', 'committing', 'crux', 'soft','sandbag', 'awkward','creative','comfortable']
safetyterms=['runout','spicy','exciting','nervous','sketchy','no pro', 'deck', 'eats gear', 'easy to protect','fall','rusty','clipping','swing', 'tenuous', 'minimal pro', 'mental']
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