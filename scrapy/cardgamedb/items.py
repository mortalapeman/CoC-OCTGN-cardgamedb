# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CardgamedbItem(Item):
    name = Field()
    type = Field()
    faction = Field()
    cost = Field()
    skill = Field()
    icons = Field()
    subtype = Field()
    gametext = Field()
    titleflavortext = Field()
    flavortext = Field()
    setacronym = Field()
    setname = Field()
    packname = Field()
    number = Field()
    illustrator = Field()
    imageurl = Field()
    struggleicons = Field()
    symbols = Field()
    specialattribute = Field()
    isunique = Field()
    cardurl = Field()
