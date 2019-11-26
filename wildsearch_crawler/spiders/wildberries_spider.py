# -*- coding: utf-8 -*-

import datetime
import scrapy
import re
import logging

from scrapy.loader import ItemLoader
from wildsearch_crawler.items import WildsearchCrawlerItem


class WildberriesSpider(scrapy.Spider):
    name = "wb"

    def start_requests(self):
        category_url = getattr(self, 'category_url', None)

        if category_url is not None:
            yield scrapy.Request(category_url, self.parse_category)

        good_url = getattr(self, 'good_url', None)

        if good_url is not None:
            yield scrapy.Request(good_url, self.parse_good)

    def parse_category(self, response):
        # follow links to goods pages
        for good_url in response.css('a.ref_goods_n_p::attr(href)'):
            yield response.follow(good_url, self.parse_good)

        # follow pagination
        for a in response.css('.pager-bottom a.next'):
            yield response.follow(a, callback=self.parse)

    def parse_good(self, response):
        def generate_reviews_link(base_url, sort='Asc'):
            # at first it is like https://www.wildberries.ru/catalog/8685970/detail.aspx
            # must be like https://www.wildberries.ru/catalog/8685970/otzyvy?field=Date&order=Asc
            return re.sub('detail\.aspx.*$', 'otzyvy?field=Date&order=' + sort, base_url)

        current_good_item = WildsearchCrawlerItem()
        parent_item = response.meta['parent_item'] if 'parent_item' in response.meta else None

        loader = ItemLoader(item=current_good_item, response=response)

        # create list of images
        image_urls = []

        for tm in (response.css('.pv-carousel .carousel a img::attr(src)')):
            image_urls.append(tm.get().strip().replace('tm', 'big'))

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
        loader.add_value('image_urls', image_urls)
        loader.add_value('wb_brand_country', wb_brand_country)
        loader.add_value('wb_manufacture_country', wb_manufacture_country)

        # fill purchase count
        # "ordersCount":1100,
        loader.add_value('wb_purchases_count', re.compile('"ordersCount":(\d+),').search(response.text)[1])

        if parent_item is not None:
            loader.add_value('wb_parent_id', parent_item.get('wb_id', ''))

        # get reviews dates
        reviews_links = [
            generate_reviews_link(response.url, 'Asc')
            # generate_reviews_link(response.url, 'Desc') Чтобы не разбираться с сохранением асинхронных запросов
        ]

        for link in reviews_links:
            yield response.follow(link, callback=self.parse_good_review_date, meta={'item': current_good_item})

        # follow goods variants only if we scrap parent item
        if parent_item is None:
            for variant in (response.css('.options ul li a')):
                yield response.follow(variant, callback=self.parse_good, meta={'parent_item': current_good_item})

        loader.load_item()

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
