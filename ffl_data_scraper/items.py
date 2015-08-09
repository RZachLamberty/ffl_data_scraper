# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FflDataScraperItem(scrapy.Item):
    ffl_source = scrapy.Field()
    playername = scrapy.Field()
    team = scrapy.Field()
    pos = scrapy.Field()
    status_type = scrapy.Field()
    passing_c = scrapy.Field()
    passing_a = scrapy.Field()
    passing_yds = scrapy.Field()
    passing_td = scrapy.Field()
    passing_int = scrapy.Field()
    rushing_r = scrapy.Field()
    rushing_yds = scrapy.Field()
    rushing_td = scrapy.Field()
    receiving_rec = scrapy.Field()
    receiving_yds = scrapy.Field()
    receiving_tot = scrapy.Field()
    pts_total = scrapy.Field()
    parsed_on = scrapy.Field()
