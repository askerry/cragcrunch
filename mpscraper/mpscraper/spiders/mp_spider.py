# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 09:51:01 2014

@author: amyskerry
"""
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
#from scrapy.spider import Spider
from scrapy.selector import Selector
from mpscraper.items import Climb, Area, Climber, Ticks, Comments, Stars, Grades, ToDos
from mpscraper.settings import timeout, cleanup
from mpscraper.cleanup import errorurls, area_urls, user_urls
import unicodedata
from scrapy.exceptions import CloseSpider
import datetime
import numpy as np
import string


#NOTE:
#to explore xpath type scrapy shell <url> in command line
#sel.xpath(...) will return extracted contents
    

routetypes=['Trad', 'Sport', 'Ice', 'Aid', 'Mixed', 'Alpine', 'Boulder', 'Toprope']

def checktime(spider):
    if spider.timeout:
        delta=datetime.datetime.now()-spider.crawlstarttime
        if delta.total_seconds()/60.0>spider.timeout:
            print "timeout"
            raise CloseSpider('passed timeout thresh')

                
class ClimbAreaSpider(CrawlSpider):
    name = "mpclimbsareas"
    #rules = [Rule(LinkExtractor(allow=["^"+url+"$" for url in urls]), callback='parseclimbsandareas', follow=following)]
    rules = [Rule(LinkExtractor(allow=['\/v\/.+\/\d+']), callback='parseclimbsandareas', follow=True)]
    def __init__(self):
        super(ClimbAreaSpider, self).__init__()
        self.timeout=timeout
        self.allowed_domains = ["mountainproject.com"]
        self.crawlstarttime=datetime.datetime.now()
        if cleanup:
            self.start_urls= errorurls
        else:
            self.start_urls = area_urls           
    
    def parseclimbsandareas(self, response): #note this needs to be named something other than parse
        if response.url in area_urls:
            return None
        checktime(self)
        sel = Selector(response)
        pagetype=checkpagetype(sel, response.url)
        if pagetype=='climb':
            climb=Climb()
            climb['url'] = afterwww(response.url)
            climb['name']=sel.xpath('//span[@itemprop="itemreviewed"]/text()').extract()[0]
            climb['area']=sel.xpath('//span[@itemprop="title"]/text()').extract()[-1]
            climb['areaurl']='mountainproject.com'+sel.xpath('//a[@itemprop="url"]/@href').extract()[-1]
            climb['region']=sel.xpath('//span[@itemprop="title"]/text()').extract()[0]
            try:
                climb['avgstars']=sel.xpath('//meta[@itemprop="average"]/@content').extract()[0]
            except:
                climb['avgstars']='unrated'
            grades1=sel.xpath('//span[@class="rateYDS"]/text()').extract()
            grades2=sel.xpath('//span[@class="rateHueco"]/text()').extract()
            grades3=sel.xpath('//td[contains(text(),"Consensus")]/following-sibling::td/text()').extract()
            if len(grades1)>0:
                climb['grade']=grades1[-1]
            elif len(grades2)>0:
                climb['grade']=grades2[-1]
            elif len(grades3)>0:
                climb['grade']=grades3[0]
            else:
                climb['grade']='unavailable'
            entries=sel.xpath('//td[contains(text(),"Type")]/following-sibling::td[1]/text()').extract()[0].split(',')
            climb['style']=entries[0]
            climb['pitch']='1 p' #assume 1 pitch unless designated otherwise
            climb['length']='unavailable'
            for e in entries[1:]:
                if 'pitch' in e:            
                    climb['pitch']=e[1:] #weird space before pitch lengths
                elif e not in routetypes and "'" in e:
                    climb['length']=e  
            ###
            try:        
                climb['fa']=sel.xpath('//td[contains(text(),"FA")]/following-sibling::td[1]/text()').extract()[0]   
            except:
                climb['fa']='unavailable'
            try:        
                climb['pageviews']=sel.xpath('//td[contains(text(),"Page Views")]/following-sibling::td[1]/text()').extract()[0]   
            except:
                climb['pageviews']='unavailable'
            climb['submittedby']=sel.xpath('//td[contains(text(),"Submitted By:")]/following-sibling::td[1]/a/text()').extract()[0]
            descrip1=sel.xpath('//h3[contains(text(),"Description")]/following-sibling::div/text()').extract()
            descrip2=sel.xpath('//h3[contains(text(),"Description")]/following-sibling::p[1]/text()').extract()
            if len(descrip1)>0: 
                climb['description']=[par for par in descrip1 if par!=' ']
            elif len(descrip2)>0: 
                climb['description']=[par for par in descrip2 if par!=' ']
            else:
                climb['description']='unavailable'
            loc1=sel.xpath('//h3[contains(text(),"Location")]/following-sibling::div/text()').extract()
            loc2=sel.xpath('//h3[contains(text(),"Location")]/following-sibling::p[1]/text()').extract()
            if len(loc1)>0:
                climb['locationdescrip']=loc1
            elif len(loc2)>0:
                climb['locationdescrip']=loc2
            else:
                climb['locationdescrip']='unavailable'
            prot1=sel.xpath('//h3[contains(text(),"Protection")]/following-sibling::div/text()').extract()
            prot2=sel.xpath('//h3[contains(text(),"Protection")]/following-sibling::p[1]/text()').extract()
            if len(prot1)>0:            
                climb['protection']=prot1
            elif len(prot2)>0:
                climb['protection']=prot2
            else:
                climb['protection']='unavailable'
            for key in climb.keys():
                try:
                    climb[key]=cleanhtml(climb[key])
                except:
                    pass
            if climb['region']=='International':
                climb['region']=cleanhtml(sel.xpath('//span[@itemprop="title"]/text()').extract()[1])
            return climb
        elif pagetype=='area':
            area=Area()
            area['url'] = afterwww(response.url)
            area['name']=sel.xpath('//h1[@class="dkorange"]/em/text()').extract()[0]
            try:
                area['area']=sel.xpath('//span[@itemprop="title"]/text()').extract()[-1]
                area['areaurl']='mountainproject.com'+sel.xpath('//a[@itemprop="url"]/@href').extract()[-1]
                area['region']=sel.xpath('//span[@itemprop="title"]/text()').extract()[0]
            except:
                area['area']='World'
                area['areaurl']='www.google.com'
                area['region']='World'
            try:
                area['maplocation']=sel.xpath('//td[contains(text(),"Location:")]/following-sibling::td[1]/text()').extract()[0]
            except:
                area['maplocation']='unavailable'
            try:
                area['mapref']=sel.xpath('//td[contains(text(),"Location:")]/following-sibling::td[1]/a/@href').extract()[0]
            except:
                area['mapref']='unavailable'
            try:
                area['elevation']=sel.xpath('//td[contains(text(),"Elevation:")]/following-sibling::td[1]/text()').extract()[0]
            except:
                area['elevation']='unavailable'
            try:        
                area['pageviews']=sel.xpath('//td[contains(text(),"Page Views")]/following-sibling::td[1]/text()').extract()[0]   
            except:
                area['pageviews']='unavailable'
            descrip1=sel.xpath('//h3[contains(text(),"Description")]/following-sibling::p[1]/text()').extract()
            descrip2=sel.xpath('//h3[contains(text(),"Description")]/following-sibling::div[1]/text()').extract()
            if len(descrip1)>0:
                area['description']=[par for par in descrip1 if par!=' ']
            elif len(descrip2)>0:
                area['description']=[par for par in descrip2 if par!=' ']
            else:
                area['description']='unavailable'
            directions1=sel.xpath('//h3[contains(text(),"Getting There")]/following-sibling::p[1]/text()').extract()
            directions2=sel.xpath('//h3[contains(text(),"Getting There")]/following-sibling::div[1]/text()').extract()
            if len(descrip1)>0:
                area['directions']=[par for par in directions1 if par!=' ']
            elif len(descrip2)>0:
                area['directions']=[par for par in directions2 if par!=' ']
            else:
                area['directions']='unavailable'
            for key in area.keys():
                try:
                    area[key]=cleanhtml(area[key])
                except:
                    pass
            if area['region']!='International':
                area['country']='USA'
            else:
                area['country']='International'
                area['region']=area['name']
            return area

        
class UserDataSpider(CrawlSpider):
    name = "mpuserdata"
    rules = [Rule(LinkExtractor(allow=['\/u\/.+\/\d+']), callback='parseuserdata', follow=True)]
    def __init__(self):
        super(UserDataSpider, self).__init__()
        self.timeout=timeout
        self.allowed_domains = ["mountainproject.com"]
        self.crawlstarttime=datetime.datetime.now()
        if cleanup:
            self.start_urls= errorurls
        else:
            self.start_urls = user_urls
    def parseuserdata(self, response):
        if response.url in user_urls:
            return None
        checktime(self)
        sel = Selector(response)
        pagetype=checkpagetype(sel, response.url)
        if pagetype=='ticks':
            ticks=Ticks()
            ticks['url'] = afterwww(response.url)
            ticks['climber'] = sel.xpath('//h1/text()').extract()[0]
            ticks['climb']=sel.xpath('//table/tr/td[1]/p/a/text()').extract()
            ticks['climblink']=sel.xpath('//table/tr/td[1]/p/a/@href').extract()
            ticks['climblink']=['mountainproject.com'+link for link in ticks['climblink'] if len(link)>0]
            notes=sel.xpath('//table/tr/td[4]/p/text()').extract()
            ticks['note']=[par for par in notes if par!=' ']
            ticks['date']=sel.xpath('//table/tr/td[5]/p/text()').extract()
            for key in ticks.keys():
                try:
                    ticks[key]=cleanhtml(ticks[key], join=False)
                except:
                    pass
            ticks['name']=ticks['url']
            return ticks
        elif pagetype=='climberinfo':
            climber=Climber()
            climbtypes=['Trad', 'Sport', 'Boulders', 'Aid', 'Ice']
            climber['url'] = afterwww(response.url)
            climber['name'] = sel.xpath('//h1/text()').extract()[0]
            try:
                climber['personal'] = sel.xpath('//div[contains(text(),"Personal:")]/em/text()').extract()[0]
            except:
                climber['personal'] = 'unavailable'
            try:
                climber['favclimbs'] = sel.xpath('//div[contains(text(),"Favorite Climbs:")]/em/text()').extract()[0]
            except:
                climber['favclimbs'] = 'unavailable'
            try:
                climber['interests'] = sel.xpath('//div[contains(text(),"Other Interests:")]/em/text()').extract()[0]
            except:
                climber['interests'] = 'unavailable'
            try:
                climber['climbstyles'] = sel.xpath('//div[contains(text(),"Likes to climb:")]/text()').extract()[0]
                climber['climbstyles']=climber['climbstyles'][15:]
            except:
                climber['climbstyles'] = 'unavailable'
            try:
                climber['moreinfo'] = sel.xpath('//div[contains(text(),"More information:")]/div/em/text()').extract()[0]
            except:
                climber['moreinfo'] = 'unavailable'
            selfreports={}        
            for climbtype in climbtypes:
                if climbtype in ['Sport', 'Trad', 'Boulders']:
                    leadstring='//div[contains(text(),"Likes to climb:")]/div/table/tr/td[contains(text(), "%s")]/following-sibling::td[1]/span/text()' %(climbtype)
                    followstring='//div[contains(text(),"Likes to climb:")]/div/table/tr/td[contains(text(), "%s")]/following-sibling::td[2]/span/text()' %(climbtype)
                else:
                    leadstring='//div[contains(text(),"Likes to climb:")]/div/table/tr/td[contains(text(), "%s")]/following-sibling::td[1]/text()' %(climbtype)
                    followstring='//div[contains(text(),"Likes to climb:")]/div/table/tr/td[contains(text(), "%s")]/following-sibling::td[2]/text()' %(climbtype)
                leadlist=sel.xpath(leadstring).extract()
                try: 
                    followlist=sel.xpath(followstring).extract()
                except:
                    followlist=None
                try: 
                    selfreports[climbtype]=[cleanhtml(leadlist), cleanhtml(followlist)]
                except:
                    pass
            for key in selfreports.keys():
                if key=='Boulders':
                    climber['boulders'] = beforeslash(selfreports['Boulders'][0])
                else:
                    climber[key.lower()+'_l'] = beforeslash(selfreports[key][0])
                    climber[key.lower()+'_f'] = beforeslash(selfreports[key][1])
            for key in climber.keys():
                try:
                    climber[key]=cleanhtml(climber[key])
                except:
                    pass
            if 'female' in climber['personal'].lower():
                climber['gender']='F'
            elif 'male' in climber['personal'].lower():
                climber['gender']='M'
            age=findintinstring(climber['personal'])
            if age:
                climber['age']=age
            return climber
        elif pagetype=='comments':
            comments=Comments()
            comments['url'] = afterwww(response.url)
            comments['climber'] = sel.xpath('//h1/text()').extract()[0]
            comments['climb']=sel.xpath('//table/tr/td[1]/p/a[contains(@href, "/v/")][last()]/text()').extract()
            numlinks=len(sel.xpath('//table/tr/td[1]/p').extract())*2
            comments['climblink']=[sel.xpath('//table/tr[%s]/td[1]/p/a/@href' %(i+3)).extract()[-2] for i in range(0,numlinks,2)]    
            #comments['climblink']=sel.xpath('//table/tr/td[1]/p/a/@href').extract()
            comments['climblink']=['mountainproject.com'+link for link in comments['climblink'] if len(link)>0]
            commentsentries=sel.xpath('//span[contains(b, "Comments:")]').extract()
            commentstxt=[e[45:-28] for e in commentsentries]
            #commentstxt=sel.xpath('//b[contains(text(), "Comments:")]/following-sibling::text()').extract()
            try:
                comments['comment']=[par for par in commentstxt if par!=' ']
            except:
                comments['comment']='unavailable'
            comments['date']=sel.xpath('//b[contains(text(), "When:")]/following-sibling::text()').extract()
            for key in comments.keys():
                try:
                    comments[key]=cleanhtml(comments[key], join=False)
                except:
                    pass
            comments['name']=comments['url']
            return comments
        elif pagetype=='stars':
            stars=Stars()
            stars['url'] = afterwww(response.url)
            stars['climber'] = sel.xpath('//h1/text()').extract()[0]
            stars['climb']=sel.xpath('//table/tr/td[1]/p/a/text()').extract()
            stars['climblink']=sel.xpath('//table/tr/td[1]/p/a/@href').extract()
            stars['climblink']=['mountainproject.com'+link for link in stars['climblink'] if len(link)>0]
            starscript=sel.xpath("//script[contains(.,'stars')]/text()").extract()
            scores=[]
            for starstring in starscript:
                try:
                    scores.append(parsestars(starstring))
                except:
                    scores.append('unavailable')
            stars['starsscore']=scores
            for key in stars.keys():
                try:
                    stars[key]=cleanhtml(stars[key], join=False)
                except:
                    pass
            stars['name']=stars['url']
            return stars
        elif pagetype=='grades':
            grades=Grades()
            grades['url'] = afterwww(response.url)
            grades['climber'] = sel.xpath('//h1/text()').extract()[0]
            grades['climb']=sel.xpath('//table/tr/td[1]/p/a/text()').extract()
            grades['climblink']=sel.xpath('//table/tr/td[1]/p/a/@href').extract()
            grades['climblink']=['mountainproject.com'+link for link in grades['climblink'] if len(link)>0]
            numentries=len(sel.xpath('//table/tr/td[3]/p').extract())
            gradeentries=[]
            for i in range(numentries):
                matchstring='//table/tr[%s]/td[3]/p/span/text()' % (i+3)
                try:
                    gradeentries.append(sel.xpath(matchstring).extract()[0])
                except:
                    gradeentries.append('unavailable')
            grades['grade']=gradeentries
            for key in grades.keys():
                try:
                    grades[key]=cleanhtml(grades[key], join=False)
                except:
                    pass
            grades['name']=grades['url']
            return grades
        elif pagetype=='todosXX':
            todos=ToDos()
            todos['url'] = afterwww(response.url)
            try:
                todos['climber'] = sel.xpath('//h1/text()').extract()[0]
            except:
                todos['climber'] = sel.xpath('//meta[@name="description"]/@content').extract()[0][30:-20]
            todos['climb']=sel.xpath('//table/tr/td[1]/a/text()').extract()
            if len(todos['climb'])>0:
                todos['climblink']=sel.xpath('//table/tr/td[1]/a/@href').extract()
                todos['climblink']=['mountainproject.com'+link for link in todos['climblink'] if len(link)>0]
                for key in todos.keys():
                    try:
                        todos[key]=cleanhtml(todos[key], join=False)
                    except:
                        pass
                todos['name']=todos['url']
                return todos
        
def checkpagetype(sel, url):
    if len(sel.xpath('//span[@itemprop="itemreviewed"]/text()').extract())>0 and len(sel.xpath('//h3[contains(text(),"Climbing Season")]/text()').extract())==0:
        pagetype='climb'
    elif len(sel.xpath('//h1[@class="dkorange"]/em/text()').extract())>0 and len(sel.xpath('//h3[contains(text(),"Climbing Season")]/text()').extract())>0:
        pagetype='area'
    elif len(sel.xpath('//h1/text()').extract())>0 and 'personalpage' in url:
        pagetype='climberinfo'
    elif 'action=ticks' in url and 'printer=1' not in url and '&export=1' not in url and 'breakdown' not in url:
        pagetype='ticks'
    elif 'what=RATING' in url and 'printer=1' not in url and 'printer=1p' not in url:
        pagetype='grades'
    elif 'what=COMMENT' in url and 'printer=1' not in url and 'printer=1p' not in url:
        pagetype='comments'
    elif 'what=SCORE' in url and 'printer=1' not in url and 'printer=1p' not in url:
        pagetype='stars'
    elif 'action=todos' in url:
        pagetype='todos'
    else:
        pagetype='uncategorized'
    return pagetype 
        
def parsestars(starstring):
    prekey='starsHtml('
    scoreindex=starstring.find(prekey)+len(prekey)
    return starstring[scoreindex]
    
def striprecursiveprint(string):
    rec='printer=1'
    if rec in string:
        string=string[:string.index(rec)+len(rec)]
    return string
    
def cleanhtml(stringfromhtml, join=True):
    stringreplacements={'Leads ': '', 'Follows ' :'', 'Likes to Climb':''}
    if type(stringfromhtml)==list:
        newstrings=[]
        for string in stringfromhtml:
            try:
                string=unicodedata.normalize('NFKD', string).encode('ascii','ignore').strip('\r\n')
            except:
                string=string.strip('\r\n')
            for rep in stringreplacements.items():
                string=string.replace(rep[0], rep[1])
            string=striprecursiveprint(string)
            newstrings.append(string)
        if join:
            newstrings='\n'.join(newstrings)
        if len(stringfromhtml)==0:
            newstrings='NULL'
    else:
        try:
            stringfromhtml=unicodedata.normalize('NFKD', stringfromhtml).encode('ascii','ignore').strip('\r\n')
        except:
            stringfromhtml=stringfromhtml.strip('\r\n')
        for rep in stringreplacements.items():
            stringfromhtml=stringfromhtml.replace(rep[0], rep[1])
        newstrings=striprecursiveprint(stringfromhtml)
    return newstrings
    
def floatorstr(string):
    try:
        float(string)
        return 1
    except:
        return 0
def findintinstring(string):
    string=np.array([el for el in string])
    indices=np.array([floatorstr(x) for x in string])
    try:
        numbers=list(string[indices==1])
        numbers=int(''.join(numbers))
        return numbers
    except:    
        return None
def beforeslash(string):
    try:
        index=string.index('\n')
        return string[:index]
    except:
        return string
def afterwww(string):
    try:
        index=string.index('www')+4
    except:
        index=string.index('://')+3
    return string[index:]