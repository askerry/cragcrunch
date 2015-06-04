'''
This module contains functions that allow for fetching (via scraping) data for specified users, climbs, or areas
'''
import sys
sys.path.append('../')
from utilities import retrieval
import utilities.randomdata as rd
import urllib2
from bs4 import BeautifulSoup
import re
import numpy as np
import prep_updates as pu

rooturl="www.mountainproject.com"


###############################
#     main fetch functions    #
###############################

def refresh_id(id_num, kind='climb'):
    url=retrieval.get_url(id_num, kind=kind)
    refresh_url(url, kind=kind, id_num=id_num)

def refresh_url(url, kind='climb', follow=True, id_num=None):
    r=urllib2.urlopen(url)
    html = r.read()
    if id_num is None:
        try:
            id_num=retrieval.get_id(url, kind)
        except:
            id_num='new'
    print id_num
    if kind=='climb':
        obj=update_climb(id_num, url, html, follow)
    elif kind=='climber':
        obj=update_climber(id_num, url, html, follow)
    elif kind=='area':
        obj=update_area(id_num, url, html, follow)
    return obj
        
def update_climb(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    statsurl=rooturl + soup.find('a', href=re.compile("ShowObjectStats")).get('href')
    counts, std=update_stats(id_num, statsurl)
    commenter_urls=[a.get('href') for a in soup.find_all('a', href=re.compile("/u/"))]
    if follow:
        for commenter in commenter_urls:
            refresh_url(rooturl+commenter, kind='climber')
    return parse_climb(id_num, soup, std)
    
def update_climber(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    climber_dict=parse_climber(id_num, soup)
    if follow:
        contrib_pages=fetch_contribs(url+'?action=contribs&')
        for kind in contrib_pages.keys():
            contrib_pages[kind]['objects']=[]
            for pagen,page in enumerate(contrib_pages[kind]['pages']):
                url=contrib_pages[kind]['urls'][pagen]
                if kind=='commenturl':
                    contrib_pages[kind]['objects'].extend(extract_comments(page, climber_dict['climberid'], climber_dict['name'], url))
                else:
                    contrib_pages[kind]['objects'].extend(extract_results(page, climber_dict['climberid'], climber_dict['name'], url, kind=kind))
        for pageset in contrib_pages.values():
            for result in pageset['objects']:
                result=pu.process(result)
    return climber_dict
    
def update_area(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    commenter_urls=[a.get('href') for a in soup.find_all('a', href=re.compile("/u/"))]
    for commenter in commenter_urls:
        print rooturl+commenter
        #refresh_url(rooturl+commenter, kind='climber')
    if follow:
        leftnav=soup.find('table', id=re.compile('leftNav'))
        if len(soup.find_all('span', id="routeSortLabel"))>0:
            climb_urls=[c.get('href') for c in leftnav.find_all('a', href=re.compile("/v/"))]
            for climb in climb_urls:
                refresh_url(climb, kind='climb', follow=False)
        else:
            area_urls=[a.get('href') for a in leftnav.find_all('a', href=re.compile("/v/"))] 
            for area in area_urls:
                refresh_url(area, kind='area', follow=False)
    return parse_area(id_num, soup) 
    
 
###############################
#       parsing functions     #
###############################
   
def parse_climb(climbid, soup, std):
    d={}
    d['climbid']=climbid
    d['name']=soup.find('title').get_text()
    areaname=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[-1].find('span').get_text()
    region=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[0].find('span').get_text()
    try:
        seconddown=region=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[1].find('span').get_text()
    except:
        seconddown=areaname
    d['area']=float(retrieval.find_area(areaname, region, seconddown))
    d['description']=str(soup.find(lambda x:under_heading(x, 'Description')).next_sibling.get_text())
    d['locationdescrip']=str(soup.find(lambda x:under_heading(x, 'Location')).next_sibling.get_text())
    d['protection']=str(soup.find(lambda x:under_heading(x, 'Protection')).next_sibling.get_text())
    summary_block=soup.find('span', id='starSummaryText').next_sibling.next_sibling
    d['grade']=str(soup.find(lambda x: 'href' in x.attrs.keys() and x.get_text()=='YDS:').next_sibling[1:])
    d['fa']=str(summary_block.find_all('tr')[2].find(lambda x:x.get_text()[:3]=='FA:').next_sibling.get_text())
    string=str(summary_block.find('td').next_sibling.next_sibling.get_text())
    d['style'],d['pitch'],d['length']=string.split(',')
    d['url']=str(soup.find('link', rel="canonical").attrs['href'])
    d['pageviews']=str(summary_block.find_all('tr')[3].find(lambda x:x.get_text()[:10]=='Page Views').next_sibling.get_text())
    d['submittedby']=str(summary_block.find_all('tr')[4].find('a').get_text())
    stars=soup.find('span', id='starSummaryText')
    d['avgstars']=str(stars.find('meta', itemprop="average")['content'])
    d['starcounts']=int(stars.find('meta', itemprop="votes")['content'])
    d['starstd']=std
    return d
    
def parse_area(areaid, soup):
    d={}
    d['areaid']=areaid
    d['name']=soup.find('h1').get_text()[:-1]
    areaname=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[-1].find('span').get_text()
    region=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[0].find('span').get_text()
    try:
        seconddown=region=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[1].find('span').get_text()
    except:
        seconddown=areaname
    d['area']=float(retrieval.find_area(areaname, region, seconddown))
    d['description']=str(soup.find(lambda x:under_heading(x, 'Description')).next_sibling.get_text())
    d['directions']=str(soup.find(lambda x:under_heading(x, 'Getting There')).next_sibling.get_text())
    d['elevation']='unavailable'
    try:
        loc_info=soup.find('h1').next_sibling.next_sibling.next_sibling.find(lambda x:x.get_text()[:3]=='Loc').next_sibling
        d['maplocation']=[val for val in loc_info.children][0][:-1]
        d['mapref']=loc_info.find('a').attrs['href']
    except:
        d['maplocation'],d['maplocation']='unavailable', 'unavailable'
    d['region']=soup.find_all('div', itemtype='http://data-vocabulary.org/Breadcrumb')[0].find('span').get_text()
    if d['region'] in rd.states.values():
        d['country']='USA'
    else:
        d['country']='International'
    d['url']=str(soup.find('link', rel="canonical").attrs['href'])
    d['pageviews']=str(soup.find('h1').next_sibling.next_sibling.next_sibling.find(lambda x:x.get_text()[:10]=='Page Views').find_all('td')[1].get_text())
    return d
    
def parse_climber(climberid, soup):
    d={}
    d['climberid']=climberid
    d['name']=soup.find('h1').get_text()[:-1]
    d['mainarea']='unavailable'
    d['url']=str(soup.find('link', rel="canonical").attrs['href'])
    personinfo=soup.find(lambda x: x.has_attr('class')  and 'personalData' in x['class'])
    personinfo.find(lambda x: x.get_text()[:9]=='Personal:').find('em').get_text()
    d['personal']=personinfo.find(lambda x: x.get_text()[:9]=='Personal:').find('em').get_text()
    if "Female" in d['personal'] or 'female' in d['personal']:
        d['gender']='F'
    elif "Male" in d['personal'] or 'male' in d['personal']:
        d['gender']='M'
    else:
        d['gender']='unavailable'
    d['age']=''.join([char for char in d['personal'] if char.isdigit()])
    return d
    
    
###############################
#       contrib functions     #
###############################

def fetch_contribs(url):
    urls={}
    urls['commenturl']=url+'&what=COMMENT&'
    urls['starurl']=url+'&what=SCORE&'
    urls['gradeurl']=url+ '&what=RATING&'
    data={}
    for key in urls.keys():
        url=urls[key]
        url_list=[url]
        r=urllib2.urlopen(url)
        html = r.read()
        soup = BeautifulSoup(html)
        for i in range(1,get_num(soup)):
            url_list.append(urls[key]+'&page='+str(i+1))
        pages=[]
        for u in url_list:
            r=urllib2.urlopen(u)
            pages.append(BeautifulSoup(r.read()))
        data[key]={'urls':url_list, 'pages':pages}
    return data
        

def extract_results(soup, climberid, climbername, url, kind='gradeurl'):
    results=[]
    for entry in soup.find_all('a', target="_top"):
        if '/v/' in entry['href'] and entry.parent.has_attr('class') and entry.parent['class'][0]!='small':
            obj_dict={}
            obj_dict['url']=url[11:]
            obj_dict['climber']=climberid
            obj_dict['climblink']=entry['href']
            obj_dict['name']=climbername+'_'+entry.get_text()
            obj_dict=check_or_fetch(obj_dict)
            if kind=='gradeurl':
                obj_dict['grade']=entry.parent.parent.next_sibling.next_sibling.find('span').get_text()
                obj_dict['gradesid']=np.nan
            elif kind=='starurl':
                string=entry.parent.parent.next_sibling.script.get_text()
                obj_dict['starsid']=np.nan
                obj_dict['starsscore']=string[string.index('starsHtml')+len('starsHtml')+1]
            results.append(obj_dict)
    return results
    
def extract_comments(soup, climberid, climbername, url):
    results=[]
    for entry in [s.parent for s in soup.find_all('b') if 'Location' in s.get_text()]:
        line=entry.find_all('a')[-2]
        if '(' in line.get_text() and ')' in line.get_text():
            obj_dict={}
            obj_dict['commentsid']=np.nan
            obj_dict['url']=url[11:]
            obj_dict['climber']=climberid
            obj_dict['climblink']=line['href']
            obj_dict=check_or_fetch(obj_dict)
            climbname=line.get_text()[:line.get_text().index('(')-1]
            obj_dict['date']=entry.find(lambda x: 'When' in x.get_text()).next_sibling
            obj_dict['comment']=entry.parent.parent.next_sibling.find('span').get_text()[10:]
            obj_dict['name']=climbername+'_'+climbname
            results.append(obj_dict)
    return results

###############################
#        miscellaneous        #
###############################            
            
def get_num(soup):
    smalls=soup.find_all('small')
    string=[sm for sm in smalls if 'Page 1 of' in sm.get_text()][0].get_text()
    return int(string[10:string.index('.')])            
            
def check_or_fetch(obj_dict):
    climblink='http://www.mountainproject.com'+obj_dict['climblink']
    climbid=retrieval.get_id(climblink, kind='climb')
    if climbid=='new':
        climb_obj=refresh_url(climblink, kind='climb')
        climb_obj=pu.process(climb_obj)
        obj_dict['climbid']=retrieval.get_id(climblink, kind='climb')
    else:
        obj_dict['climbid']=climbid
    return obj_dict


def under_heading(tag, heading):
    return tag.has_attr('class') and tag['class'][0]=='dkorange' and tag.get_text()[:-1]==heading


def update_stats(climbid, statsurl):
    return 0,0


    