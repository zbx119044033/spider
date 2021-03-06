# -*- coding:utf-8 -*-
# spider for vobao product 1

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


class VobaoSpider(scrapy.Spider):
    name = "vobao_pro1"
    allowed_domains = ["p.vobao.com"]
    start_urls = ["http://p.vobao.com/-_0_0_0_0-0_0---1/list_%d.shtml" % i for i in range(1, 500)]

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
        item["domain"] = "insurance products from p.vobao.com"

        interest = []
        for sel in response.xpath("//div[3]/table[2]/tbody/tr"):
            interest.append(
                {"保障项目": my_strip(sel.xpath("td[1]/text()").extract_first()),
                 "保额": my_strip(sel.xpath("td[2]/text()").extract_first()),
                 "说明": my_strip(sel.xpath("td[3]/text()").extract_first())})

        classification = []
        for sel in response.xpath("//div[1]/div[2]/div[2]/div[2]/dl/dt/a"):
            classification.append(my_strip(sel.xpath("text()").extract_first()))

        others = ""
        for sel in response.xpath("//div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/p"):
            content = my_strip(sel.xpath("string(.)").extract_first())
            others += content + "."

        item["props"] = [
            {"name": "承保公司", "alias": ["公司"],
             "value": my_strip(response.xpath("//div[1]/div[1]/div[1]/dl/dt/text()").extract()[1])},
            {"name": "承保年龄", "alias": ["年龄"],
             "value": my_strip(response.xpath("//div[1]/div[2]/div[2]/div[2]/div[2]/ul/li[3]/text()").extract_first())},
            {"name": "保险期间", "alias": ["保期"],
             "value": my_strip(response.xpath("//div[1]/div[2]/div[2]/div[2]/div[2]/ul/li[1]/text()").extract_first())},
            {"name": "产品特色", "alias": ["产品特点"],
             "value": my_strip(response.xpath("//div[1]/div[1]/div[1]/dl/dd[1]/text()").extract()[1])},
            {"name": "支付方式", "alias": ["缴费方式"],
             "value": my_strip(response.xpath("//div[2]/ul/li[2]/text()").extract_first())},
            {"name": "保障利益", "alias": ["保障范围", "保险责任", "保障权益", "保障利益", "保险项目"], "value": interest},
            {"name": "产品类型", "alias": ["险种"], "value": classification},
            {"name": "投保须知", "alias": ["须知", "温馨提示", "责任免除"], "value": others},
            {"name": "保费", "alias": ["价格"],
             "value": my_strip(response.xpath("//div[3]/table[1]/tbody/tr[2]/td[5]/text()").extract_first())},
        ]

        for i in range(len(item["props"]) - 1, -1, -1):
            if item["props"][i]["value"] == "":
                del item["props"][i]

        print 'successfully parsed ' + str(response.url)
        yield item
