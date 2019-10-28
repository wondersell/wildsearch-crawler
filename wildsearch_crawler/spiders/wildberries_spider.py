import scrapy

class WildberriesSpider(scrapy.Spider):
    name = "wb"
    start_urls = [
        "https://www.wildberries.ru/catalog/dom-i-dacha/instrumenty/krany-sharovye"
    ]

    def parse(self, response):
        # follow links to goods pages
        for good_url in response.css('a.ref_goods_n_p::attr(href)'):
            yield response.follow(good_url, self.parse_good)

    def parse_good(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'url': response.url,
            'name': extract_with_css('.brand-and-name .name::text'),
            'brand': extract_with_css('.brand-and-name .brand::text'),
            'image': extract_with_css('.preview-photo::attr(src)')
        }