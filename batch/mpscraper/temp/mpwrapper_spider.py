# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 10:18:20 2014

@author: amyskerry
"""
import sys
sys.path.append('/users/amyskerry/documents/projects/cragcrunch/mpscraper/')
from scrapy.utils.project import get_project_settings
from mp_spider import CommentSpider
from scrapy.crawler import Crawler
from scrapy import log

from twisted.internet import reactor

def setup_crawler():
    spider = CommentSpider()
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()

setup_crawler()
log.start()
reactor.run()