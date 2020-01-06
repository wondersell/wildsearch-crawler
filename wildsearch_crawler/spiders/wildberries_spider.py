# -*- coding: utf-8 -*-

import datetime
import logging
import scrapy
import requests
import re

from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItemWildberries

# включаем логи
logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class WildberriesSpider(scrapy.Spider):
    name = "wb"

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)

            return

        good_url = getattr(self, 'good_url', None)

        if good_url is not None:
            yield scrapy.Request(good_url, self.parse_good)

            return

        # default – start crawl from sitemap
        yield scrapy.Request("https://www.wildberries.ru/services/karta-sayta", self.parse_sitemap)

    def parse(self, response):
        pass

    def parse_sitemap(self, response):
        for url in response.css('#sitemap a::attr(href)'):
            yield response.follow(url, self.parse_category)

    def parse_category(self, response):
        def clear_url_params(url):
            return url.split('?')[0]

        def parse_id_from_url(url):
            return url.split('/')[4]

        wb_category_position = int(response.meta['current_position']) if 'current_position' in response.meta else 1
        wb_category_url = clear_url_params(response.url)

        allow_dupes = getattr(self, 'allow_dupes', False)
        skip_details = getattr(self, 'skip_details', False)

        # follow links to goods pages
        for item in response.css('.catalog-content .j-card-item'):
            good_url = item.css('a.ref_goods_n_p::attr(href)')

            if skip_details:
                current_good_item = WildsearchCrawlerItemWildberries()
                loader = ItemLoader(item=current_good_item, response=response)

                loader.add_value('wb_id', parse_id_from_url(good_url.get()))
                loader.add_value('product_name', item.css('.goods-name::text').get())
                loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
                loader.add_value('marketplace', 'wildberries')
                loader.add_value('product_url', clear_url_params(good_url.get()))
                loader.add_value('wb_category_url', wb_category_url)
                loader.add_value('wb_category_position', wb_category_position)
                loader.add_value('wb_brand_name', item.css('.brand-name::text').get())

                yield loader.load_item()
            else:
                yield response.follow(clear_url_params(good_url.get()), self.parse_good, dont_filter=allow_dupes, meta={
                    'current_position': wb_category_position,
                    'category_url': wb_category_url
                })

            wb_category_position += 1

        # follow pagination
        for a in response.css('.pager-bottom a.next'):
            yield response.follow(a, callback=self.parse_category, meta={'current_position': wb_category_position})

    def parse_good(self, response):
        def clear_url_params(url):
            return url.split('?')[0]

        def generate_reviews_link(base_url, sort='Asc'):
            # at first it is like https://www.wildberries.ru/catalog/8685970/detail.aspx
            # must be like https://www.wildberries.ru/catalog/8685970/otzyvy?field=Date&order=Asc
            return re.sub('detail\.aspx.*$', 'otzyvy?field=Date&order=' + sort, base_url)

        skip_images = getattr(self, 'skip_images', False)
        skip_variants = getattr(self, 'skip_variants', False)
        allow_dupes = getattr(self, 'allow_dupes', False)

        current_good_item = WildsearchCrawlerItemWildberries()
        parent_item = response.meta['parent_item'] if 'parent_item' in response.meta else None

        loader = ItemLoader(item=current_good_item, response=response)

        # category position stats
        wb_category_url = response.meta['category_url'] if 'category_url' in response.meta else None
        wb_category_position = response.meta['current_position'] if 'current_position' in response.meta else None

        canonical_url = response.css('link[rel=canonical]::attr(href)').get()

        if canonical_url != response.url:
            yield response.follow(clear_url_params(canonical_url), self.parse_good, dont_filter=allow_dupes,  meta={
                'current_position': wb_category_position,
                'category_url': wb_category_url
            })

            return

        # scraping brand and manufacturer countries
        wb_brand_country = ''
        wb_manufacture_country = ''

        for param in (response.css('.params .pp')):
            param_name = param.css('span:nth-of-type(1) b::text').get()
            param_value = param.css('span:nth-of-type(2)::text').get()

            if u'Страна бренда' == param_name:
                wb_brand_country = param_value

            if u'Страна производитель' == param_name:
                wb_manufacture_country = param_value

        # fill css selectors fields
        loader.add_css('product_name', '.brand-and-name .name::text')
        loader.add_css('wb_reviews_count', '.count-review i::text')
        loader.add_css('wb_price', '.final-cost::text')
        loader.add_css('wb_rating', '.product-rating span::text')
        loader.add_css('wb_id', 'div.article span::text')

        # fill non-css values
        loader.add_value('parse_date', datetime.datetime.now().isoformat(" "))
        loader.add_value('marketplace', 'wildberries')
        loader.add_value('product_url', response.url)
        loader.add_value('wb_brand_name', response.css('.brand-and-name .brand::text').get())
        loader.add_value('wb_brand_url', response.css('.brandBannerImgRef::attr(href)').get())
        loader.add_value('wb_brand_country', wb_brand_country)
        loader.add_value('wb_manufacture_country', wb_manufacture_country)
        loader.add_value('wb_category_url', wb_category_url)
        loader.add_value('wb_category_position', wb_category_position)

        # create list of images
        if skip_images is False:
            image_urls = []

            for tm in (response.css('.pv-carousel .carousel a img::attr(src)')):
                image_urls.append(tm.get().strip().replace('tm', 'big'))

            loader.add_value('image_urls', image_urls)

        # fill purchase count
        # "ordersCount":1100,
        loader.add_value('wb_purchases_count', re.compile('"ordersCount":(\d+),').search(response.text)[1])

        if parent_item is not None:
            loader.add_value('wb_parent_id', parent_item.get('wb_id', ''))

        '''
        # get reviews dates
        reviews_links = [
            generate_reviews_link(response.url, 'Asc')
            generate_reviews_link(response.url, 'Desc')  # Чтобы не разбираться с сохранением асинхронных запросов
        ]

        for link in reviews_links:
            yield response.follow(link, callback=self.parse_good_review_date, meta={'item': current_good_item})
        '''

        # follow goods variants only if we scrap parent item
        if skip_variants is False and parent_item is None:
            for variant in (response.css('.options ul li a::attr(href)')):
                yield response.follow(clear_url_params(variant.get()), callback=self.parse_good, meta={
                    'parent_item': current_good_item
                })

        yield loader.load_item()

    def parse_good_review_date(self, response):
        loader = ItemLoader(item=response.meta['item'], response=response)

        comment_blocks = response.css('#Comments .comment')

        date_type = None

        if re.compile('^.*order=Asc$').match(response.url):
            date_type = 'wb_first_review_date'

        if re.compile('^.*order=Desc$').match(response.url):
            date_type = 'wb_last_review_date'

        if len(comment_blocks) > 0 and date_type is not None:
            loader.add_value(date_type, comment_blocks[0].css('.time::attr(content)').get())

        yield loader.load_item()

    def closed(self, reason):
        callback_url = getattr(self, 'callback_url', None)
        callback_params = {}

        for element in getattr(self, 'callback_params', None).split('&'):
            k_v = element.split('=')
            callback_params[k_v[0]] = callback_params[k_v[1]]

        if callback_url is not None:
            logger.info(f"Noticed callback_url in params, sending POST request to {callback_url}")
            requests.post(callback_url, data=callback_params)
