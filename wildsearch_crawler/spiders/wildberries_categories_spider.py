import datetime
import logging
import scrapy

from .base_spider import BaseSpider
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class WildberriesCategoriesSpider(BaseSpider):
    name = "wb_categories"

    def start_requests(self):
        yield scrapy.Request('https://www.wildberries.ru/menu/getrendered?lang=ru&burger=true', self.parse_main_menu, headers={'x-requested-with': 'XMLHttpRequest'})

    def parse_main_menu(self, response):
        # start_url_parsed = urlparse(response.request.url)

        for url in response.css('a'):
            #url_parsed = urlparse(url.attrib['href'])
            #full_url = urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'wildberries',
                'wb_category_name': url.css('::text').get(),
                'wb_category_url': url.attrib['href']
            }
