#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: espn_spider.py
Author: zlamberty
Created: 2015-08-09

Description:
    spider for scraping espn's website

Usage:
    <usage>

"""

import logging
import scrapy

from ffl_data_scraper.items import FflDataScraperItem
from ffl_data_scraper.psql import wipe_raw_data
from scrapy.conf import settings


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

logger = logging.getLogger(__name__)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

class EspnSpider(scrapy.Spider):
    name = 'espn'

    def __init__(self, wipeTable=False):
        super(EspnSpider, self).__init__()
        self.allowed_domains = ['espn.go.com']
        self.leagueid = settings.get('LEAGUE_ID')
        self.start_urls = [
            "http://games.espn.go.com/ffl/tools/projections?&leagueId={}".format(self.leagueid)
        ]
        if wipeTable:
            wipe_raw_data(source=self.name)

    def parse(self, response):
        playerrows = response.xpath('//tr[contains(@class, "pncPlayerRow")]')
        for player in playerrows:
            item = FflDataScraperItem()
            item['ffl_source'] = self.name

            playerText = player.xpath('./td/text()').extract()
            # -- remapped to 0.0 by my own convention
            playerText = [el.replace('--', '0') for el in playerText]

            pn = player.xpath('./td[@class="playertablePlayerName"]')[0]
            item['playername'] = pn.xpath('./a/text()')[0].extract()

            tp = pn.xpath('text()').extract()[0].replace(', ', '')
            tps = [el for el in tp.split(u'\xa0') if el]
            try:
                [team, pos] = tps
            except ValueError:
                team = ''
                pos = tps[0]
            item['team'] = team
            item['pos'] = pos

            item['status_type'] = playerText[2]

            item['passing_c'], item['passing_a'] = [
                float(el) for el in playerText[3].split('/')
            ]

            item['passing_yds'] = float(playerText[4])
            item['passing_td'] = float(playerText[5])
            item['passing_int'] = float(playerText[6])
            item['rushing_r'] = float(playerText[7])
            item['rushing_yds'] = float(playerText[8])
            item['rushing_td'] = float(playerText[9])
            item['receiving_rec'] = float(playerText[10])
            item['receiving_yds'] = float(playerText[11])
            item['receiving_tot'] = float(playerText[12])

            totpts = player.xpath('./td[@class="playertableStat appliedPoints"]/text()')[0].extract().replace('--', '0')
            item['pts_total'] = float(totpts)

            yield item

        nextLinks = response.xpath('//div[@class="paginationNav"]/a[text() = "NEXT"]')
        if nextLinks:
            url = nextLinks[0].xpath('@href')[0].extract()
            url = response.urljoin(url)
            yield scrapy.Request(url, self.parse)
