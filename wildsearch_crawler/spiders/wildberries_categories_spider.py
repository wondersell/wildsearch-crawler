# -*- coding: utf-8 -*-

import datetime

import scrapy
import requests


class WildberriesCategoriesSpider(scrapy.Spider):
    name = "wb_categories"
    start_urls = ['https://www.wildberries.ru/services/karta-sayta']

    def parse(self, response):
        for url in response.css('#sitemap a'):
            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'wildberries',
                'wb_category_name': url.css('::text').get(),
                'wb_category_url': url.attrib['href']
            }

    def closed(self, reason):
        callback_url = getattr(self, 'callback_url', None)
        callback_params = {}

        for element in getattr(self, 'callback_params', None).split('&'):
            k_v = element.split('=')
            callback_params[k_v[0]] = callback_params[k_v[1]]

        if callback_url is not None:
            requests.post(callback_url, data=callback_params)