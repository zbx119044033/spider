# -*- coding:utf-8 -*-
# spider for cngold agency

import scrapy
import re
from product.items import ProductItem


class CngoldSpider(scrapy.Spider):
    name = "gold_agency"
    allowed_domains = ["insurance.cngold.org"]
    start_urls = ["https://insurance.cngold.org/bxym", ]
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'product.middlewares.spidermiddlewares.ProductSpiderMiddleware': 10,
        },
        'ITEM_PIPELINES': {
            'product.pipelines.pipeline.FilterPipeline': 300,
            'product.pipelines.pipeline.JsonWriterPipeline': 800,
            # 'product.pipelines.pipeline.MongoPipeline': 800,
        }
    }

    def parse(self, response):
        next_pages = response.xpath("//div[@class='company']/a/@href").extract()
        # print "next_pages=", next_pages
        for next_page_url in next_pages:
            if re.match(r'(https://insurance.cngold.org/bxym/index_\d{4}.html)', next_page_url):
                # print "next_url=", next_page_url
                yield scrapy.Request(next_page_url, callback=self.parse_item, dont_filter=True)

    def parse_item(self, response):
        item = ProductItem()
        item["name"] = response.xpath("//div[@class='p-m']/h2/a/text()").extract_first()
        item["alias"] = []
        item["domain"] = "agency from insurance.cngold.org"
        item["props"] = [
            {"name": "link", "value": response.xpath("//div[@class='p-m']/h2/a/@href").extract_first()},
            {"name": "desc", "value": response.xpath("//div[@class='p-m']/p[1]").extract_first().strip("</p>\\rn").strip()}
        ]
        print 'successfully parsed ' + str(response)
        yield item
