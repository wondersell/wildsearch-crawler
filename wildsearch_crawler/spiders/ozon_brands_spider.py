import datetime
import logging
from urllib.parse import urljoin, urlparse

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class WildberriesBrandsSpider(BaseSpider):
    name = "ozon_brands"
    start_urls = ['https://www.ozon.ru/brand/en--a/']

    def parse(self, response):
        for url in response.css('.b5y7 a'):
            if url.css('::text').get() != 'Все':
                yield response.follow(url, callback=self.parse_letter)

    def parse_letter(self, response):
        start_url_parsed = urlparse(response.request.url)

        for url in response.css('.b5x9 a'):
            url_parsed = urlparse(url.attrib['href'])
            full_url = urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'ozon',
                'ozon_brand_name': url.css('::text').get(),
                'ozon_brand_url': full_url
            }
