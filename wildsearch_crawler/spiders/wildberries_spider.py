# -*- coding: utf-8 -*-

import scrapy

class WildberriesSpider(scrapy.Spider):
    name = "wb"

    start_urls = [
        "https://www.wildberries.ru/catalog/aksessuary/perchatki-i-varezhki/mitenki?pagesize=100"
    ]

    def parse(self, response):
        # follow links to goods pages
        for good_url in response.css('a.ref_goods_n_p::attr(href)'):
            yield response.follow(good_url, self.parse_good)

        # follow pagination
        for a in response.css('.pager-bottom a.next'):
            yield response.follow(a, callback=self.parse)

    def parse_good(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        # follow goods variants
        for variant in (response.css('.options ul li a')):
            yield response.follow(variant, callback=self.parse_good)

        # create list of images
        image_urls = []

        for th in (response.css('.pv-carousel .carousel a img::attr(src)')):
            image_urls.append(th.get().strip().replace('tm', 'big'))

        yield {
            'marketplace': 'wildberries',
            'product_url': response.url,
            'product_name': extract_with_css('.brand-and-name .name::text'),
            'image_urls': image_urls,
            'wb_id': extract_with_css('div.article span::text'),
            'wb_reviews_count': extract_with_css('.count-review i::text'),
            'wb_purchases_count': extract_with_css('.j-orders-count::text'), # не работает, отрисовывается JS после рендера страницы
            'wb_price': extract_with_css('.final-cost::text'),
            'wb_rating': extract_with_css('.product-rating span::text')
        }