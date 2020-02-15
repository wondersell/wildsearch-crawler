import datetime
import logging
import scrapy
import extruct
import json

from urllib.parse import quote
from .base_spider import BaseSpider
from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemOzon

logger = logging.getLogger(__name__)


class WildberriesSpider(BaseSpider):
    name = "ozon"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY':  1.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0
    }

    def convert_category_url_to_api(self, url):
        """Simple trick to get JSON with LOTS of data instead of HTML is to convert URL as follows:

        From /category/utyugi-10680/?layout_container=categoryMegapagination&layout_page_index=9&page=9
        To  https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=%2Fcategory%2Futyugi-10680%2F%3Flayout_container%3DcategoryMegapagination%26layout_page_index%3D8%26page%3D8
        """
        return f'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={quote(url)}'

    def add_pagination_params(self, url):
        """Trick to get first result page with pagination and 'nextPage' param"""
        return f'{url}?layout_container=categorySearchMegapagination&layout_page_index=1&page=1'

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            category_url_parametrized = self.add_pagination_params(category_url)

            yield scrapy.Request(
                self.convert_category_url_to_api(category_url_parametrized),
                self.parse_category,
                meta={
                    'category_url': category_url
                }
            )

            return

        good_url = getattr(self, 'good_url', None)

        if good_url is not None:
            yield scrapy.Request(good_url, self.parse_good_page)

            return

        # default – start crawl from sitemap
        #yield scrapy.Request("https://www.wildberries.ru/services/karta-sayta", self.parse_sitemap)

    def parse(self, response):
        pass

    def parse_category(self, response):
        def find_goods_items(data):
            """We search for following patterns in JSON keys:

            searchResultsV2-226897-default-1
            searchResultsV2-193750-categorySearchMegapagination-2
            """
            for idx, val in data['widgetStates'].items():
                if 'searchResultsV2' in idx:
                    return val

        category_url = response.meta['category_url'] if 'category_url' in response.meta else None
        category_position = int(response.meta['current_position']) if 'current_position' in response.meta else 1

        category_data = json.loads(response.text)

        items_raw = find_goods_items(category_data)
        items = json.loads(items_raw)
        items_count = len(items['items'])

        current_position = category_position

        for item in items['items']:
            current_position += 1

            yield {
                'parse_date': datetime.datetime.now().isoformat(" "),
                'marketplace': 'ozon',
                'product_name': item['cellTrackingInfo']['title'],
                'product_url': item['link'],
                'image_urls': item['images'],
                'ozon_id': item['cellTrackingInfo']['id'],
                'ozon_category_url': category_url,
                'ozon_category_name': item['cellTrackingInfo']['category'],
                'ozon_category_position': current_position,
                'ozon_reviews_count': None,
                'ozon_price': item['cellTrackingInfo']['finalPrice'],
                'ozon_rating': None,
                'ozon_manufacture_country': None,
                'ozon_first_review_date': None,
                'ozon_last_review_date': None
            }

        # follow pagination
        if 'nextPage' in [*category_data]:
            yield scrapy.Request(
                self.convert_category_url_to_api(category_data['nextPage']),
                self.parse_category,
                meta={
                    'category_url': category_url,
                    'category_position': category_position + items_count
                }
            )

    def parse_good_page(self, response):
        def find_json_ld_by_type(page_metadata, block_type):
            """Is there a better way to write this?"""
            for block in page_metadata['json-ld']:
                if block['@type'] == block_type:
                    return block

        current_good_item = WildsearchCrawlerItemOzon()
        loader = ItemLoader(item=current_good_item, response=response)

        page_metadata = extruct.extract(response.text, base_url=response.url, uniform=True)

        product_meta = find_json_ld_by_type(page_metadata, 'Product')

        # fill non-css values
        loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
        loader.add_value('marketplace', 'ozon')
        loader.add_value('product_name',  product_meta['name'])
        loader.add_value('product_url', response.url)
        loader.add_value('image_urls', None)
        loader.add_value('ozon_id', product_meta['sku'])
        loader.add_value('ozon_category_url', None)
        loader.add_value('ozon_category_name', None)
        loader.add_value('ozon_category_position', None)
        loader.add_value('ozon_reviews_count', None)
        loader.add_value('ozon_price', product_meta['offers']['Price'].replace(u'\xa0', ''))
        loader.add_value('ozon_rating', response.css('div.product-rating-simple::attr(title)').get())
        loader.add_value('ozon_manufacture_country', None)
        loader.add_value('ozon_first_review_date', None)
        loader.add_value('ozon_last_review_date', None)

        yield loader.load_item()
