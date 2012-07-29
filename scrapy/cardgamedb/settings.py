# Scrapy settings for cardgamedb project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'cardgamedb'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['cardgamedb.spiders']
NEWSPIDER_MODULE = 'cardgamedb.spiders'
DEFAULT_ITEM_CLASS = 'cardgamedb.items.CardgamedbItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
DOWNLOAD_DELAY = 0.5
COOKIES_ENABLED = False
ROBOTSTXT_OBEY = True

