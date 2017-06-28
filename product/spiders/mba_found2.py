# -*- coding:utf-8 -*-
# spider for mba lib foundation except for "保险术语", uncompleted and it did not work

import scrapy
from product.items import ProductItem
import re
import string
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def my_strip(s):
    if s is None:
        return None
    else:
        res = s.replace("\r", "").replace("\t", "").replace("\n;", "").strip(string.punctuation).strip()
        return re.sub("<[^>]*?>", "", res)


class Mba2Spider(scrapy.Spider):
    name = "mba_found2"
    allowed_domains = ["wiki.mbalib.com/wiki"]
    start_urls = ["http://wiki.mbalib.com/wiki/Category:保险市场",
                  "http://wiki.mbalib.com/wiki/Category:保险种类",
                  "http://wiki.mbalib.com/wiki/Category:保险合同",
                  "http://wiki.mbalib.com/wiki/Category:保险原则",
                  "http://wiki.mbalib.com/wiki/Category:保险关系人",
                  "http://wiki.mbalib.com/wiki/Category:保险准备金",
                  "http://wiki.mbalib.com/wiki/Category:保险费率",
                  "http://wiki.mbalib.com/wiki/Category:保险营销",
                  "http://wiki.mbalib.com/wiki/Category:保险单",
                  "http://wiki.mbalib.com/wiki/Category:保险统计",
                  ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
            'product.middlewares.downloader.UAPool': 390,
            'product.middlewares.downloader.JavaScriptMiddleware': 410,
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
        urls = response.xpath("//span[@class='mbttle BaoName']/a/@href").extract()
        for url in urls:
            full_url = response.urljoin(url)
            print "content_page=", full_url
            yield scrapy.Request(full_url, callback=self.parse_item, dont_filter=True)

    def parse_item(self, response):
        item = ProductItem()
        item["name"] = response.xpath("//h1/text()").extract_first()
        alias = []
        item["alias"] = alias
        item["domain"] = "insurance foundation from wiki.mbalib"
        item["props"] = [
            {"name": "link", "value": response.url},
            {"name": "desc",
             "value": my_strip(response.xpath("//*[@id='bodyContent']/p[1]/text()").extract_first())},
        ]
        print 'successfully parsed ' + str(response.url)
        yield item
