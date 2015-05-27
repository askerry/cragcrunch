'''
This module contains functions that allow for fetching (via scraping) data for specified users, climbs, or areas
'''

import retrieval
import urllib2
from bs4 import BeautifulSoup
import re

rooturl="www.mountainproject.com"

def refresh_id(id_num, kind='climb'):
    url=retrieval.get_url(id_num, kind=kind)
    refresh_url(url, kind=kind, id_num=id_num)

def refresh_url(url, kind='climb', follow=True, id_num=None):
    r=urllib2.urlopen(url)
    html = r.read()
    if id_num is None:
        id_num=get_id(url, kind)
    if kind=='climb':
        obj=update_climb(id_num, url, html, follow)
    elif kind=='climber':
        obj=update_climber(id_num, url, html, follow)
    elif kind=='area':
        obj=update_area(id_num, url, html, follow)
        
def update_climb(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    statsurl=rooturl + soup.find('a', href=re.compile("ShowObjectStats")).get('href')
    counts, std, update_stats(id_num, statsurl)
    commenter_urls=[a.get('href') for a in soup.find_all('a', href=re.compile("/u/"))]
    for commenter in commenter_urls:
        refresh_url(commenter, kind='climber')
    return parse_climb(id_num, soup, counts, std)
    
def update_climber(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    return climb

def update_area(id_num, url, html, follow):
    soup = BeautifulSoup(html)
    commenter_urls=[a.get('href') for a in soup.find_all('a', href=re.compile("/u/"))]
    for commenter in commenter_urls:
        refresh_url(commenter, kind='climber')
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
    
def parse_climb(climbid, soup, counts, std):
    return climb
    
def parse_area(areaid, soup):
    return area
    
def update_stats(climbid, statsurl):
    pass
        
def get_id(url, kind='climb'):
    '''takes a url and returns matching id from the relevant table'''
    return id_num
    