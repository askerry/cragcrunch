# Scrapy settings for mpscraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mpscraper'

SPIDER_MODULES = ['mpscraper.spiders']
NEWSPIDER_MODULE = 'mpscraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'askerry'

ITEM_PIPELINES = {
    'mpscraper.pipelines.DBPipeline': 100
}

LOG_LEVEL='WARNING'

DEPTH_LIMIT=1

###AES settings 
timeout=500 #spider will timeout after this many minutes. set to None for infinite crawling/crawling until completion
cleanup=False

