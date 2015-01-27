__author__ = 'amyskerry'

import numpy as np
import pandas as pd

routetypes=['Trad', 'Sport', 'Toprope', 'Boulder', 'Ice', 'Miaxed', 'Aid', 'Alpine']
holdterms=['crimp','pinch','jug','sloper','ledge','pocket','sidepull','dyno', 'deadpoint','heelhook','toehook','bat-hang', 'undercling', 'crack', 'flake', 'arete','gaston', 'layback','handcrack', 'flaringcrack','fingerscrack', 'widecrack','thincrack', 'offwidth', 'chimney','diahedral','corner', 'traverse']
descriptors=['steep','overhung','slab','technical','thin', 'ramp','sporty','vertical', 'boulder']
easeterms=['easy','hard','stiff','pump','beginner','hung','take','difficult', 'committing', 'crux', 'soft','sandbag', 'awkward','creative','comfortable']
safetyterms=['runout','spicy','exciting','nervous','sketchy','pro', 'deck', 'gear', 'protect','fall','rusty','clipping','swing', 'tenuous', 'nopro', 'mental']
rockterms=['granite', 'limestone', 'schist', 'patina','sandstone', 'conglomerate', 'quartzite', 'gneiss', 'basalt']



terms=holdterms+descriptors+easeterms+safetyterms+rockterms
termtypes={'rock type':rockterms, 'ease factors':easeterms, 'hold types':holdterms,'safety factors': safetyterms, 'face descriptions':descriptors}


def convertsqlobj2df(sqllist):
    '''takes list of objects returned by sqlalchemy and converts to dataframe'''
    cols=[col for col in sqllist[0].__dict__.keys() if col !='_sa_instance_state']
    data={col:[] for col in cols}
    for obj in sqllist:
        for col in cols:
            data[col].append(obj.__dict__[col])
    return pd.DataFrame(data=data)

def convertsdictlist2df(dictlist):
    '''takes list of dictionaries and converts to dataframe'''
    cols=dictlist[0].keys()
    data={col:[] for col in cols}
    for d in dictlist:
        for col in cols:
            data[col].append(d[col])
    return pd.DataFrame(data=data)
