# -*- coding: utf-8 -*-

import datetime
import scrapy
import re
import logging

from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemOzon

class OzonSpider(scrapy.Spider):
    name = "ozon"

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)

            return

        good_url = getattr(self, 'good_url', None)

        if good_url is not None:
            yield scrapy.Request(good_url, self.parse_good)

            return

    def parse_category(self, response):
        return ''

    def parse_good(self, response):
        return ''