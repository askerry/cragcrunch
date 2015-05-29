
def get_attrs(obj):
    import inspect
    attrs,_=zip(*inspect.getmembers(object, lambda x: not inspect.ismethod(x)))
    attrs=[a for a in attrs if a[:2]!='__']
    return attrs

def nanify(obj, attrs, nanvalues=['','None','unavailable', None]):
    for attr, value in obj_dict.items():
        if valuein nanvalues:
            obj_dict[attr]= np.nan
    return obj_dict
    
def string_clean(obj_dict, function, cols):
    for col in cols:
        if col in obj_dict:
            obj_dict[col]= function(obj_dict[attr])
    return obj_dict
    
def longlat(obj_dict):
    if 'maplocation' in obj_dict:
        obj_dict['latitude']= prep.getlat(obj_dict['maplocation'])
        obj_dict['longitude']= prep.getlong(obj_dict['maplocation'])
    return obj_dict
    
def extract_name(obj_dict):
    if 'url' in obj_dict:
        obj_dict['urlname'], prep.extractname(obj_dict['url']))
    return obj_dict
    

def full_obj_clean(obj_dict)
    obj_dict=string_clean(obj_dict, lambda x:int(x), ('climbid', 'areaid', 'climberid', 'ticksid', 'commentsid', 'gradesid', 'starid', 'climb', 'climber', 'area'))
    obj_dict=string_clean(obj_dict, lambda x:float(x), ('starsscore', 'age', 'avgstars'))
    obj_dict=string_clean(obj_dict, prep.removecomma, ('pageviews'))
    obj_dict=string_clean(obj_dict, prep.striplength, ('elevation', 'length'))
    obj_dict=string_clean(obj_dict, prep.pitch, ('pitch'))
    for attr,valye in obj_dict.items():
        if isinstance(value,str):
            obj_dict[attr]= prepstrip(obj_dict[attr])
    obj_dict=longlat(obj, attrs)
    obj_dict=string_clean(obj_dict, prep.mergeiceandsnow, ('style'))
    obj_dict=string_clean(obj_dict, prep.strippitch, ('pitch'))
return obj_dict

def update_hits(climberid,climbid):
    pass

def climb_in_db(climbid):
    return True
    
#this should be something that reads directly from database
def get_area_name(areaid):
    return name
    
def check_climbers_area(climberid):
    return areaid
    
def quantize_grades(obj_dict):
    obj_dict['numerizedgrade']=prep.numerizegrades(obj_dict['grade'], gradelists=[rd.grades, rd.bouldergrades])
    obj_dict['numgrade']=prep.splitgrade(obj_dict['grade'], output='num')
    obj_dict['lettergrade']=prep.splitgrade(obj_dict['grade'], output='letter')
    return obj_dicts
    
def process_stars(starscore):
    obj_dict['extracted_avgstars']=starscore
    obj_dict['starsscore']=starscore
    obj_dict['computed_avgstars']=starscore
    return obj_dict



def process(obj, add=True):
    obj_dict=full_obj_clean(obj_dict)
    if 'climbid' in obj_dict and !climb_in_db(obj_dict['climbid']):
        #fetch and save climb
    if 'style' in obj_dict and is_silly_style(obj_dict['style']):
        return False
    if 'style' in obj_dict and (not is_graded(obj_dict['grade'], obj_dict['style']) or np.isnan(obj_dict['area'])):
        return False
    if 'age' in obj_dict 
        if obj_dict['age']>120:
            obj_dict['area']=check_climbers_area(obj_dict['climberid'])
            obj_dict['region'], obj_dict['mainarea']=find_state_and_main(obj_dict['area'])
        obj_dict['mainarea']
    if 'climberid' in obj_dict and 'climbid' in obj_dict:
        update_hits(obj_dict['climberid'], obj_dict['climbid'])
    if 'grade' in obj_dict:
        obj_dict=quantize_grades(obj_dict)
    if 'style' in obj_dict:
        obj_dict['region'], obj_dict['mainarea']=find_state_and_main(obj_dict['area'])
        obj_dict['mainarea_name']=get_area_name(obj_dict['mainarea']) 
        feature_dict=prep.load_text_feats()
        obj_dict['mainarea']=prep.text_processing(obj_dict['description'], feature_dict)
    if 'avgstar' in obj_dict:
        obj_dict=process_stars(obj_dict['avgstars'])
    retrieval.save_update_to_db(obj)
    return True
