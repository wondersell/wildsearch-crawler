import datetime
import logging
import scrapy
import requests

from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class WildberriesCategoriesSpider(scrapy.Spider):
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

    def closed(self, reason):
        callback_url = getattr(self, 'callback_url', None)
        callback_params_raw = getattr(self, 'callback_params', None)
        callback_params = {}

        if callback_params_raw is not None:
            for element in callback_params_raw.split('&'):
                k_v = element.split('=')
                callback_params[str(k_v[0])] = k_v[1]

        if callback_url is not None:
            logger.info(f"Noticed callback_url in params, sending POST request to {callback_url}")
            requests.post(callback_url, data=callback_params)