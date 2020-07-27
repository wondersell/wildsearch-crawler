import scrapy
import logging
import datetime
import re
import geopy.distance

from .base_spider import BaseSpider
from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemProductcenterProducer
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class ProductcenterProducersSpider(BaseSpider):
    name = "stolberi"

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)
            return

        # default – start crawl from front page
        yield scrapy.Request("https://msk.stolberi.ru", self.parse_front)

    def parse(self, response):
        pass

    def parse_front(self, response):
        def add_region_to_url(url):
            region_filter = getattr(self, 'only_region', None)
            if region_filter is not None and region_filter not in url:
                url = url.replace('/producers', '/producers/' + region_filter)
            return url

        def add_domain_to_url(url):
            start_url_parsed = urlparse(response.request.url)
            url_parsed = urlparse(url)
            return urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

        for menu_item in response.css('.hcm_producers li ul li'):
            category_url = add_domain_to_url(add_region_to_url(menu_item.css('a:nth-of-type(1)::attr(href)').get()))
            category_name = menu_item.css('a:nth-of-type(1)::text').get()

            yield response.follow(category_url, callback=self.parse_category, meta={
                'category_url': category_url,
                'category_name': category_name,
            })

    def parse_category(self, response):
        def clear_url_params(url):
            return url.split('?')[0]

        def add_domain_to_url(url):
            start_url_parsed = urlparse(response.request.url)
            url_parsed = urlparse(url)
            return urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

        category_url = response.meta['category_url'] if 'category_url' in response.meta else clear_url_params(response.url)
        category_name = response.meta['category_name'] if 'category_name' in response.meta else response.css('h1::text').get()

        # parse products
        for product in response.css('.product'):
            yield {
                'id': product.css('.product__img::attr(id)').get(),
                'url': add_domain_to_url(product.css('.product__img a.product__a::attr(href)').get()),
                'category_name': category_name,
                'category_url': add_domain_to_url(category_url),
                'name': product.css('.product__title a.product__a::text').get(),
                'price': product.css('.prices__actual::text').get(),
            }

        # follow pagination
        for a in response.css('.pagination__a'):
            yield response.follow(a, callback=self.parse_category)
