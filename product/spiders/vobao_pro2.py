# -*- coding:utf-8 -*-
# spider for vobao product 2

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


class VobaoSpider(scrapy.Spider):
    name = "vobao_pro2"
    allowed_domains = ["p.vobao.com"]
    start_urls = ["http://p.vobao.com/-1_0_0_0_0-0_0---1/list_%d.shtml" % i for i in range(1, 407)]

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
        urls = response.xpath("//span[@class='mbttle BaoName']/a/@href").extract()
        for url in urls:
            full_url = response.urljoin(url)
            print "content_page=", full_url
            yield scrapy.Request(full_url, callback=self.parse_item, dont_filter=True)

    def parse_item(self, response):
        item = ProductItem()
        item["name"] = response.xpath("//h2/span[1]/text()").extract_first()
        alias = []
        item["alias"] = alias
        item["domain"] = "insurance products from p.vobao.com2"
        item["props"] = [
            {"name": "承保公司", "alias": ["公司"],
             "value": my_strip(response.xpath("//div[1]/div[1]/div[1]/dl/dt/text()").extract()[1])},
            {"name": "承保年龄", "alias": ["年龄"], "value": None},
            {"name": "保险期间", "alias": ["保期"], "value": None},
            {"name": "产品特色", "alias": ["产品特点"],
             "value": my_strip(response.xpath("//div[1]/div[1]/div[1]/dl/dd[1]/text()").extract()[1])},
            {"name": "支付方式", "alias": ["缴费方式"], "value": None},
            {"name": "保障利益", "alias": ["保障范围", "保险责任", "保障权益", "保障利益", "保险项目"], "value": None},
            {"name": "产品类型", "alias": ["险种"], "value": None},
            {"name": "投保须知", "alias": ["须知", "温馨提示", "责任免除"], "value": None},
            {"name": "保费", "alias": ["价格"], "value": None},
        ]

        for i in range(len(item["props"]) - 1, -1, -1):
            if item["props"][i]["value"] is None:
                del item["props"][i]

        print 'successfully parsed ' + str(response.url)
        yield item

