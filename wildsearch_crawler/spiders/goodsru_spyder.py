import logging
import re

import scrapy

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class GoodsRuSpider(BaseSpider):
    name = 'goodsru'

    def start_requests(self):
        yield scrapy.Request('https://goods.ru/catalog/details/generator-startvolt-lg-08l4-100024234597/',
                             self.parse_details_page)

    def parse_details_page(self, response):
        article = response.css('div.prod--art:first-of-type').get()
        article = re.sub('\n', '', article)
        article = re.sub('\s', '', article)
        article = re.sub('<spanclass="space"></span>', '', article)
        article = re.sub('<divclass="prod--art">Артикул', '', article)
        article = re.sub('</div', '', article)

        yield {
            'article': article,
            'vendor_code': response.css('span[itemprop=productID]::text').get()
        }
