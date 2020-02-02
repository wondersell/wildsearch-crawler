import datetime
import logging

from .base_spider import BaseSpider
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class WildberriesBrandsSpider(BaseSpider):
    name = "wb_brands"
    start_urls = ['https://www.wildberries.ru/wildberries/brandlist.aspx?letter=a']

    def parse(self, response):
        for url in response.css('.brands-by-letter-list a'):
            yield response.follow(url, callback=self.parse_letter)

    def parse_letter(self, response):
        start_url_parsed = urlparse(response.request.url)

        for url in response.css('.i-brand-list a'):
            url_parsed = urlparse(url.attrib['href'])
            full_url = urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'wildberries',
                'wb_brand_name': url.css('span::text').get(),
                'wb_brand_url': full_url,
                'wb_image_url': url.css('img::attr(src)').get()
            }
