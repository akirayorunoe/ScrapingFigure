# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FigureItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    hash = scrapy.Field()
    date = scrapy.Field()
    
