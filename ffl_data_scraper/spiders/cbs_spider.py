#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: cbs_spider.py
Author: zlamberty
Created: 2015-08-09

Description:
    spider for scraping cbs's website

Usage:
    <usage>

"""

import logging
import re
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

class CbsSpider(scrapy.Spider):
    name = 'cbs'

    def __init__(self, wipeTable=False):
        super(CbsSpider, self).__init__()
        self.allowed_domains = ['cbssports.com']
        self.start_urls = [
            "http://fantasynews.cbssports.com/fantasyfootball/stats/weeklyprojections/{}/season/avg/ppr?&print_rows=9999".format(poskey)
            for poskey in ['QB', 'RB', 'WR', 'TE']
        ]
        self.passkeys = [
            'passing_c', 'passing_a', 'passing_yds', 'passing_td', 'passing_int'
        ]
        self.rushkeys = ['rushing_r', 'rushing_yds', 'rushing_td']
        self.reckeys = ['receiving_rec', 'receiving_yds', 'receiving_tot']
        if wipeTable:
            wipe_raw_data(source=self.name)

    def parse(self, response):
        try:
            pos = re.match(
                '.*weeklyprojections/(QB|RB|WR|TE)/season.*',
                response.url
            ).groups()[0]
        except:
            logger.error("Couldn't find position in this url...")
            logger.debug('url = {}'.format(response.url))
            return

        playerrows = response.xpath(
            '//table[@class="data"]/tr[contains(@class, "row") and not(@id)]'
        )

        for player in playerrows:
            item = FflDataScraperItem()
            item['ffl_source'] = self.name

            playerText = player.xpath('./td/text()').extract()

            item['playername'] = player.xpath('./td/a/text()')[0].extract()

            item['team'] = team = playerText[0].replace(u',\xa0', '')
            item['pos'] = pos

            item['status_type'] = 'FA'
            item['pts_total'] = float(playerText[-1])

            if pos == 'QB':
                item['passing_c'] = float(playerText[2])
                item['passing_a'] = float(playerText[1])
                item['passing_yds'] = float(playerText[3])
                item['passing_td'] = float(playerText[4])
                item['passing_int'] = float(playerText[5])
                item['rushing_r'] = float(playerText[8])
                item['rushing_yds'] = float(playerText[9])
                item['rushing_td'] = float(playerText[11])

                for k in self.reckeys:
                    item[k] = 0.0

            elif pos == 'RB':
                item['rushing_r'] = float(playerText[1])
                item['rushing_yds'] = float(playerText[2])
                item['rushing_td'] = float(playerText[4])
                item['receiving_rec'] = float(playerText[5])
                item['receiving_yds'] = float(playerText[6])
                item['receiving_tot'] = float(playerText[8])

                for k in self.passkeys:
                    item[k] = 0.0

            elif pos in ['WR', 'TE']:
                item['receiving_rec'] = float(playerText[1])
                item['receiving_yds'] = float(playerText[2])
                item['receiving_tot'] = float(playerText[4])

                for k in self.passkeys + self.rushkeys:
                    item[k] = 0.0

            yield item
