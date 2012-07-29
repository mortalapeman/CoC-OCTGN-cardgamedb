import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.url import urlparse
from ..items import CardgamedbItem

from IPython.core.debugger import Tracer; _bp = Tracer()

class ParsingHelper:
    
    def parse_li(self, hxs, spider):
        item = CardgamedbItem()
        rel = hxs.select('./div[@class="mobileheight"]/a/@rel').extract()[0]
        item['name'] = hxs.select('./div[@class="mobileheight"]/a/@title').extract()[0]
        ustr = unicode(hxs.select('./div[@class="mobileheight"]/a/text()').extract()[0])
        item['isunique'] = u'\u2022' in ustr
        item['imageurl'] = self.get_imageurl(rel)
        self.parse_li_text(item, hxs)
        url = hxs.select('./div[@class="mobileheight"]/a/@href').extract()[0]
        item['cardurl'] = url
        spider.log('Url to follow: %s' % (url))
        return Request(url, callback=spider.parse_cardpage, dont_filter=True, meta={ 'item' : item })
    
    def filter_value(self, val, text):
            matches = [x for x, y in enumerate(text) if val in y]
            if len(matches) == 1:
                i = matches[0]
                result = text[i+1]
                text.remove(text[i])
                if result == '<br>':
                    return ''
                text.remove(result)
                return result
            else:
                return ''
        
    def parse_li_text(self, item, hxs):
        text = hxs.select('./div[2]/node()').extract()
        text = map(lambda x: x.strip(), text)
        item['cost'] = self.filter_value('Cost:', text)
        item['skill'] = self.filter_value('Skill:', text)
        item['type'] = self.filter_value('Type:', text)
        item['icons'] = self.filter_value('Icon:', text)
        item['setacronym'] = self.filter_value('Set:', text).upper()
        item['illustrator'] = self.filter_value('Illustrator:', text)
        item['faction'] = self.filter_value('Faction:', text)
        item['specialattribute'] = self.filter_value('Special Attribute:', text)
        item['symbols'] = self.filter_value('Symbols:', text)
        def get_subtype(text):
            matches = [re.search(r'<b><i>([^<>]+)</i></b>', x) for x in text]
            matches = [x for x in matches if x]
            if len(matches) > 0:
                text.remove(matches[0].group())
            return matches[0].groups()[0] if len(matches) > 0 else ''
        item['subtype'] = get_subtype(text)
        def get_flavortext(text):
            matches = [re.search(r'^<i>([^<>]+)</i>$', x) for x in text]
            matches = [x for x in matches if x]
            if len(matches) > 0:
                text.remove(matches[0].group())
            return matches[0].groups()[0] if len(matches) > 0 else ''
        item['flavortext'] = get_flavortext(text)
        text = [x for x in text if x != '<br>']
        item['gametext'] = '\r\n'.join(text)
        
    def parse_breadcrumbs(self, hxs):
        text_list = hxs.select('//div[@class="clearfix"]/ol//li/a/span/text()').extract()
        names = text_list[3:]
        return names if len(names) == 2 else [names[0], '']
    
    def get_imageurl(self, rel):
        path = rel.split('|')[0]
        return urlparse.urljoin('http://www.cardgamedb.com/forums/uploads/', path)


class CardGameDBSpider2(BaseSpider):
    name = 'CoC'
    allowed_domains = ['www.cardgamedb.com']
    start_urls = [
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=ct&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=ha&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=mi&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=sh&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=si&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=sy&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=ag&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=yo&',
                  'http://www.cardgamedb.com/index.php/CoC/coccardsearch.html?faction=ne&',
                  ]
    helper = ParsingHelper()
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # Select all list elements that have card data.
        li_list = hxs.select('//div[@class="general_box"]/ul//li[contains(@class,"hentry1")]')
        for li in li_list:
            yield self.helper.parse_li(li, self)
    
    def parse_cardpage(self, response):
        item = response.meta['item']
        hxs = HtmlXPathSelector(response)
        item['setname'], item['packname'] = self.helper.parse_breadcrumbs(hxs)
        text = hxs.select('//table[@class="ipb_table"]/tr/td/div[2]/node()').extract()
        text = [x.strip() for x in text]
        text = [x for x in text if x != '']
        item['number'] = self.helper.filter_value('Number:', text)
        def get_titleflavortext(text):
            result = re.search('<i>([^<>]+)</i>', text[2])
            return result.groups()[0] if result else ''
        item['titleflavortext'] = get_titleflavortext(text)
        return item

