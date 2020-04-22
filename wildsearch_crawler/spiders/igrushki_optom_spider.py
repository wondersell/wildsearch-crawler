import scrapy
import logging
import datetime

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class IgrushkiOptomSpider(BaseSpider):
    name = 'igrushki_optom'

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)
            return

        good_url = getattr(self, 'good_url', None)

        if good_url is not None:
            yield scrapy.Request(good_url, self.parse_good_page)
            return

        yield scrapy.Request("https://xn-----glctbckdqtalee9agek8fse.xn--p1ai/", self.parse_front)

    def parse(self, response):
        pass

    def parse_front(self, response):
        for a in response.css('a.menu-dropdown-link'):
            yield response.follow(a, callback=self.parse_category)

    def parse_category(self, response):
        for a in response.css('.product-categories a'):
            yield response.follow(a, callback=self.parse_category)

        for a in response.css('.products-view-name a'):
            yield response.follow(a, callback=self.parse_good_page)

        # follow pagination
        for a in response.css('.pagenumberer-next'):
            yield response.follow(a, callback=self.parse_category)

    def parse_good_page(self, response):
        dimensions = response.css('.details-dimensions .details-param-value::text').get()

        if dimensions is not None:
            dimensions = str.strip(dimensions)

        yield {
            'parse_date': datetime.datetime.now().isoformat(" "),
            'marketplace': 'igrushki-optom',
            'id': response.css('.details-sku .details-param-value::text').get(),
            'product_url': response.url,
            'price': response.css('.price-number::text').get(),
            'dimensions': dimensions,
            'weight': response.css('.details-param-value-weight::text').get(),
        }
