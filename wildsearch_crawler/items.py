# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(text):
    text = text.replace(u'\u00a0', '')

    text = text.replace(u'\u20bd', '')

    return text


def clear_reviews_count(text):
    text = text.replace('отзыва', '')
    text = text.replace('отзывов', '')
    text = text.replace('отзыв', '')

    return text


class WildsearchCrawlerItemWildberries(scrapy.Item):
    parse_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    marketplace = scrapy.Field(
        output_processor=TakeFirst()
    )
    product_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    product_name = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    image_urls = scrapy.Field()
    features = scrapy.Field()
    wb_id = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_parent_id = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_category_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_category_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_category_position = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_reviews_count = scrapy.Field(
        input_processor=MapCompose(clear_reviews_count, str.strip),
        output_processor=TakeFirst()
    )
    wb_purchases_count = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_price = scrapy.Field(
        input_processor=MapCompose(str.strip, clear_price),
        output_processor=TakeFirst()
    )
    wb_rating = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_brand_name = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_brand_logo = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_brand_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_brand_country = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_manufacture_country = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    wb_first_review_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_last_review_date = scrapy.Field(
        output_processor=TakeFirst()
    )

class WildsearchCrawlerItemWildberriesCategory(scrapy.Item):
    parse_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    marketplace = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_category_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_category_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    wb_category_level = scrapy.Field(
        output_processor=TakeFirst()
    )

class WildsearchCrawlerItemOzon(scrapy.Item):
    parse_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    marketplace = scrapy.Field(
        output_processor=TakeFirst()
    )
    product_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    product_name = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    image_urls = scrapy.Field()
    ozon_id = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    ozon_category_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    ozon_category_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    ozon_category_position = scrapy.Field(
        output_processor=TakeFirst()
    )
    ozon_reviews_count = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    ozon_price = scrapy.Field(
        input_processor=MapCompose(str.strip, clear_price),
        output_processor=TakeFirst()
    )
    ozon_rating = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    ozon_manufacture_country = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    ozon_first_review_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    ozon_last_review_date = scrapy.Field(
        output_processor=TakeFirst()
    )

class WildsearchCrawlerItemProductcenterProducer(scrapy.Item):
    parse_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    marketplace = scrapy.Field(
        output_processor=TakeFirst()
    )
    category_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    category_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_about = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_address = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_coords = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_distance = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_phone = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_email = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_website = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_goods_count = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_logo = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_rating = scrapy.Field(
        output_processor=TakeFirst()
    )
    producer_price_lists = scrapy.Field()