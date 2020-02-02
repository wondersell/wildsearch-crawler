import datetime
import logging

from .base_spider import BaseSpider
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class WildberriesCategoriesSpider(BaseSpider):
    name = "wb_categories"
    start_urls = ['https://www.wildberries.ru/services/karta-sayta']

    def parse(self, response):
        start_url_parsed = urlparse(response.request.url)

        for url in response.css('#sitemap a'):
            url_parsed = urlparse(url.attrib['href'])
            full_url = urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'wildberries',
                'wb_category_name': url.css('::text').get(),
                'wb_category_url': full_url
            }
