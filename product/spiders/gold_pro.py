# -*- coding:utf-8 -*-
# spider for cngold product, the price is always 20, which may involve JS and Phantom.

import scrapy
import re
from product.items import ProductItem
import sys
import string
reload(sys)
sys.setdefaultencoding('utf8')


def my_strip(s):
    if s is None:
        return None
    else:
        res = s.replace("\r", "").replace("\t", "").replace("\n;", "").strip(string.punctuation).strip()
        return re.sub("<[^>]*?>", "", res)


class CngoldSpider(scrapy.Spider):
    name = "gold_pro"
    allowed_domains = ["insurance.cngold.org"]

    start_urls = ["https://insurance.cngold.org/sgapp/ins/product/index_1_1_1_0_1.htm?labStr=1",
                  "https://insurance.cngold.org/sgapp/ins/product/index_2_1_1_0_1.htm?labStr=2",
                  "https://insurance.cngold.org/sgapp/ins/product/index_3_1_1_0_1.htm?labStr=3",
                  "https://insurance.cngold.org/sgapp/ins/product/index_4_1_1_0_1.htm?labStr=4",
                  "https://insurance.cngold.org/sgapp/ins/product/index_5_1_1_0_1.htm?labStr=5",
                  "https://insurance.cngold.org/sgapp/ins/product/index_6_1_1_0_1.htm?labStr=6",
                  "https://insurance.cngold.org/sgapp/ins/product/index_7_1_1_0_1.htm?labStr=7",
                  "https://insurance.cngold.org/sgapp/ins/product/index_8_1_1_0_1.htm?labStr=8",
                  ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'product.middlewares.downloader.UAPool': 390,
            'product.middlewares.downloader.JavaScriptMiddleware': 400,
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
        urls = response.xpath("//h3/a/@href").extract()
        for url in urls:
            if re.match(r'https://insurance.cngold.org/sgapp/ins/product/info_0.htm\?id=\d{3,4}', url):
                print "content_page=", url
                yield scrapy.Request(url, callback=self.parse_item, dont_filter=True)

        next_page_url = response.xpath(u"//a[contains(text(), '下一页')]/@href").extract_first()
        if next_page_url:
            print "next_page=", next_page_url
            yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)

    def parse_item(self, response):
        item = ProductItem()
        item["name"] = response.xpath("//h3/a[@title]/text()").extract_first()
        alias = []
        item["alias"] = alias
        item["domain"] = "insurance products from insurance.cngold.org"

        interest = []
        for sel in response.xpath("//table[2]/tbody/tr"):
            interest.append({"保障项目": my_strip(sel.xpath("th/text()").extract_first()),
                             "保额": my_strip(sel.xpath("td/text()").extract_first())})

        others = []
        for sel in response.xpath("//table[3]/tbody/tr"):
            others.append({"说明": my_strip(sel.xpath("th/text()").extract_first()),
                           "内容": my_strip(sel.xpath("td/text()").extract_first())})

        item["props"] = [
            {"name": "承保公司", "alias": ["公司"],
             "value": my_strip(response.xpath("//img/@alt[1]").extract_first())},
            {"name": "承保年龄", "alias": ["年龄"],
             "value": my_strip(response.xpath("//table[1]/tbody/tr[1]/td/text()").extract_first())},
            {"name": "保险期间", "alias": ["保期"],
             "value": my_strip(response.xpath("//table[1]/tbody/tr[2]/td/text()").extract_first())},
            {"name": "产品特色", "alias": ["产品特点"],
             "value": my_strip(response.xpath("//table[1]/tbody/tr[5]/td/text()").extract_first())},
            {"name": "支付方式", "alias": ["缴费方式"],
             "value": my_strip(response.xpath("//table[1]/tbody/tr[6]/td/text()").extract_first())},
            {"name": "保障利益", "alias": ["保障范围", "保险责任", "保障权益", "保障利益", "保险项目"], "value": interest},
            {"name": "产品类型", "alias": ["险种"], "value": None},
            {"name": "投保须知", "alias": ["须知", "温馨提示", "责任免除"], "value": others},
            {"name": "保费", "alias": ["价格"],
             "value": my_strip(response.xpath("//p[@class='arial clearfix red2']/span/text()").extract_first())},
        ]

        for i in range(len(item["props"])-1, -1, -1):
            if item["props"][i]["value"] is None:
                del item["props"][i]

        print 'successfully parsed ' + response.url
        yield item
