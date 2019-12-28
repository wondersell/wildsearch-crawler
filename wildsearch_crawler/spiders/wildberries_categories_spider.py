# -*- coding: utf-8 -*-

import datetime
import scrapy
import re
import logging

from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemWildberriesCategory

class WildberriesCategoriesSpider(scrapy.Spider):
    name = "wb_categories"
    start_urls = ['https://www.wildberries.ru/services/karta-sayta']

    def parse(self, response):
        for url in response.css('#sitemap a'):
            category = WildsearchCrawlerItemWildberriesCategory()
            loader = ItemLoader(item=category, response=response)

            loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
            loader.add_value('marketplace', 'wildberries')

            loader.add_value('wb_category_name', url.css('::text').get())
            loader.add_value('wb_category_url', url.attrib['href'])
            loader.add_value('wb_category_level', None)

            yield loader.load_item()