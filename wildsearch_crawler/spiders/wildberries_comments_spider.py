import json
import logging
import re

import dukpy
import scrapy
from scrapy.exceptions import CloseSpider

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class WildberriesCommentsSpider(BaseSpider):
    name = "wb_comments"

    def start_requests(self):
        good_url = getattr(self, 'good_url', None)

        yield scrapy.Request(good_url, self.parse_good)

    def parse(self, response):
        pass

    def parse_good(self, response):
        products_data_js = response.xpath('//script[contains(., "wb.spa.init")]/text()').get()
        products_data_js = re.sub('\n', '', products_data_js)
        products_data_js = re.sub(r'\s{2,}', '', products_data_js)

        products_data_js = re.sub('routes: routes,', '', products_data_js)
        products_data_js = re.sub('routesDictionary: routesDictionary,', '', products_data_js)

        products_init = re.findall(r'wb\.spa\.init\(({.*?})\);', products_data_js)[0]

        if products_init is not None and str(products_init) != '':
            interpreter = dukpy.JSInterpreter()
            evaled_data = interpreter.evaljs(f'init={products_init};init.router;')

            if 'ssrModel' in evaled_data.keys():
                imt_id = evaled_data['ssrModel']['product']['imtId']


        step = 1000
        skip = 0

        while True:
            request_body = {
                "imtId": imt_id,
                "skip": skip,
                "take": step,
                "order": "dateAsc"
            }

            yield scrapy.Request("https://public-feedbacks.wildberries.ru/api/v1/feedbacks/site",
                                 self.parse_comments_request, method="POST", body=json.dumps(request_body))

            skip += step

    def parse_comments_request(self, response):
        feedbacks = json.loads(response.text)

        if feedbacks['feedbacks'] is None:
            raise CloseSpider('End of feedbacks reached')

        for feedback in feedbacks['feedbacks']:
            yield {
                'text': feedback['text'],
                'rating': feedback['productValuation'],
                'created_at': feedback['createdDate'],
            }
