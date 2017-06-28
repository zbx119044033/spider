# -*- coding:utf-8 -*-
# spider for mba lib foundation on "保险术语", the desc is empty and IP is banned

import scrapy
from product.items import ProductItem
import re
import string
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def my_strip(s):
    if s is None:
        return ""
    else:
        res = s.replace("\r", "").replace("\t", "").replace("\n;", "").strip(string.punctuation).strip()
        return re.sub("<[^>]*?>", "", res)


class MbaSpider(scrapy.Spider):
    name = "mba_found"
    allowed_domains = ["wiki.mbalib.com/wiki"]
    start_urls = ["http://wiki.mbalib.com/wiki/Category:保险术语"]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
            'product.middlewares.downloader.UAPool': 390,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
            # 'product.middlewares.downloader.IPPool': 740,
        },
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
        urls = response.xpath("//tr/td/ul/li/a/@href").extract()
        for url in urls:
            full_url = response.urljoin(url)
            print "content_page=", full_url
            yield scrapy.Request(full_url, callback=self.parse_item, dont_filter=True)
        next_page_url = response.xpath(u"//a[contains(text(), '后200条')]/@href").extract_first()
        if next_page_url:
            next_page = response.urljoin(next_page_url)
            print "next_page=", next_page
            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

    def parse_item(self, response):
        item = ProductItem()
        item["name"] = response.xpath("//h1/text()").extract_first()
        alias = []
        item["alias"] = alias
        item["domain"] = "insurance foundation from wiki.mbalib"

        sel = response.xpath("//*[@id='bodyContent']/p[2]/text()")
        desc = my_strip(sel.xpath("string(.)").extract_first())

        item["props"] = [
            {"name": "link", "value": response.url},
            {"name": "desc", "value": desc},
        ]
        print 'successfully parsed ' + str(response.url)
        yield item
