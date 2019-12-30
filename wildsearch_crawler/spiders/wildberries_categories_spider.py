# -*- coding: utf-8 -*-

import datetime

import scrapy
import requests

from scrapy.utils import iterators
from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemWildberriesCategory

class WildberriesCategoriesSpider(scrapy.Spider):
    name = "wb_categories"
    start_urls = ['https://www.wildberries.ru/services/karta-sayta']

    def parse(self, response):
        for url in response.css('#sitemap a'):
            #category = WildsearchCrawlerItemWildberriesCategory()
            #loader = ItemLoader(item=category, response=response)

            #loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
            #loader.add_value('marketplace', 'wildberries')

            #loader.add_value('wb_category_name', url.css('::text').get())
            #loader.add_value('wb_category_url', url.attrib['href'])
            #loader.add_value('wb_category_level', None)

            #yield loader.load_item()
            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'wildberries',
                'wb_category_name': url.css('::text').get(),
                'wb_category_url': url.attrib['href']
            }

    def closed(self, reason):
        callback_url = getattr(self, 'callback_url', None)

        if callback_url is not None:
            requests.post(callback_url)