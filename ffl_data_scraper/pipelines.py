# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import logging

from .psql import connect
from scrapy.conf import settings


logger = logging.getLogger(__name__)


class FflDataScraperPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        self.conn = connect()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        sql = """
            insert into raw_data ( ffl_source, playername, team, pos,
              status_type, passing_c, passing_a, passing_yds, passing_td,
              passing_int, rushing_r, rushing_yds, rushing_td, receiving_rec,
              receiving_yds, receiving_tot, pts_total, parsed_on
            )
            values ( %(ffl_source)s, %(playername)s, %(team)s, %(pos)s,
              %(status_type)s, %(passing_c)s, %(passing_a)s, %(passing_yds)s,
              %(passing_td)s, %(passing_int)s, %(rushing_r)s, %(rushing_yds)s,
              %(rushing_td)s, %(receiving_rec)s, %(receiving_yds)s,
              %(receiving_tot)s, %(pts_total)s, %(parsed_on)s
            );
        """
        item['parsed_on'] = datetime.datetime.now()

        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug("attempting insert")
                cur.execute(sql, item)
                self.conn.commit()
                logger.debug("status: {}".format(self.conn.status))

        return item
