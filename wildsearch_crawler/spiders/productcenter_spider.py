import scrapy
import logging
import datetime
import requests
import re
import geopy.distance

from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemProductcenterProducer
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class ProductcenterProducersSpider(scrapy.Spider):
    name = "productcenter_producers"

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)
            return

        producer_url = getattr(self, 'producer_url', None)

        if producer_url is not None:
            yield scrapy.Request(producer_url, self.parse_producer)
            return

        # default – start crawl from front page
        yield scrapy.Request("https://productcenter.ru", self.parse_front)

    def parse_front(self, response):
        def add_region_to_url(url):
            region_filter = getattr(self, 'only_region', None)

            if region_filter is not None and region_filter not in url:
                url = url.replace('/producers', '/producers/' + region_filter)

            return url

        for url in response.css('.hcm_producers li a'):
            yield response.follow(add_region_to_url(url.attrib['href']), self.parse_category)

    def parse_category(self, response):
        def clear_url_params(url):
            return url.split('?')[0]

        category_url = response.meta['category_url'] if 'category_url' in response.meta else clear_url_params(response.url)
        category_name = response.css('h1')

        for producer_card in response.css('#content .items .item'):
            producer_goods_count = producer_card.css('a[title="Все товары производителя"]::text').get()

            yield response.follow(producer_card.css('a.link'), callback=self.parse_producer, meta={
                'category_url': category_url,
                'category_name': category_name,
                'producer_goods_count': producer_goods_count
            })

        # follow pagination
        for a in response.css('.page_links a:last-child'):
            yield response.follow(a, callback=self.parse_category, meta={
                    'category_url': category_url,
                    'category_name': category_name
                })

    def parse_producer(self, response):
        def clear_url_params(url):
            return url.split('?')[0]

        def get_address():
            return str(' ').join((
                response.css('span[itemprop="addressRegion"]::text').get(),
                response.css('span[itemprop="addressLocality"]::text').get(),
                response.css('span[itemprop="streetAddress"]::text').get()
            ))

        def add_domain_to_url(url):
            start_url_parsed = urlparse(response.request.url)
            url_parsed = urlparse(url)
            return urljoin(start_url_parsed.scheme + '://' + start_url_parsed.netloc, url_parsed.path)

        def prepare_coords(coords_str):
            coords_str = coords_str.replace(' ', '')
            return map(float, coords_str.split(','))

        current_producer_item = WildsearchCrawlerItemProductcenterProducer()

        loader = ItemLoader(item=current_producer_item, response=response)

        category_url = response.meta['category_url'] if 'category_url' in response.meta else None
        category_name = response.meta['category_name'] if 'category_name' in response.meta else None
        producer_goods_count = response.meta['producer_goods_count'] if 'producer_goods_count' in response.meta else None

        canonical_url = response.css('link[rel=canonical]::attr(href)').get()

        if canonical_url != response.url:
            yield response.follow(clear_url_params(canonical_url), self.parse_producer)
            return

        # fill css selectors fields
        loader.add_css('producer_name', 'h1.cfix::text')
        loader.add_css('producer_about', '#box_description .box_text')
        loader.add_css('producer_phone', 'span[itemprop="telephone"]::text')
        loader.add_css('producer_email', 'span[itemprop="email"]::text')
        loader.add_css('producer_website', '#producer_link::text')

        # fill non-css values
        loader.add_value('category_url', category_url)
        loader.add_value('category_name', category_name)
        loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
        loader.add_value('producer_url', response.url)
        loader.add_value('producer_address', get_address())
        loader.add_value('producer_logo', add_domain_to_url(response.css('a.fancybox[data-fancybox-group="producer"]::attr(href)').get()))
        loader.add_value('producer_goods_count', producer_goods_count)
        loader.add_value('producer_rating', '')

        producer_price_lists = []

        for price_list_url in (response.css('#box_files a')):
            producer_price_lists.append(add_domain_to_url(price_list_url.attrib['href']))

        loader.add_value('producer_price_lists', producer_price_lists)

        coords_producer = re.compile('coordinates: \[(\d+\.\d+, \d+\.\d+)]').search(response.text)[1]
        loader.add_value('producer_coords', coords_producer)

        coords_office = getattr(self, 'office_coords', None)

        if coords_office is not None:
            coords_office = prepare_coords(coords_office)
            coords_producer = prepare_coords(coords_producer)
            loader.add_value('producer_distance', round(geopy.distance.vincenty(coords_office, coords_producer).km, 2))

        yield loader.load_item()

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

