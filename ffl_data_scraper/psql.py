#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: psql.py
Author: zlamberty
Created: 2015-08-09

Description:
    wrapper for connections to psql client

Usage:
    <usage>

"""

import logging
import psycopg2

from scrapy.conf import settings


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

logger = logging.getLogger(__name__)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def connect():
    return psycopg2.connect(
        user=settings.get('PG_USER'),
        dbname=settings.get('PG_DBNAME'),
        host=settings.get('PG_HOST'),
        password=settings.get('PG_PASSWORD')
    )


def wipe_raw_data(source=None):
    logger.warning("DROPPING raw_data table!!")
    with connect() as conn:
        with conn.cursor() as cur:
            if source:
                cur.execute('DELETE FROM raw_data WHERE source = %s ;', source)
            else:
                cur.execute('DELETE FROM raw_data;')
            logger.debug("status: {}".format(conn.status))
