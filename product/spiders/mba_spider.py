# -*- coding:utf-8 -*-
# report TCPTimeOutError but does work

import scrapy
import re
from product.items import ProductItem


class MbaSpider(scrapy.Spider):
    name = "mba"
    allowed_domains = ["wiki.mbalib.com/wiki"]
    start_urls = ["http://wiki.mbalib.com/wiki/Category:保险公司",]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
            'product.middlewares.downloader.UAPool': 390,
            'product.middlewares.downloader.JavaScriptMiddleware': 410,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
            'product.middlewares.downloader.IPPool': 740,
        },
        'ITEM_PIPELINES': {
            'product.pipelines.pipeline.FilterPipeline': 300,
            'product.pipelines.pipeline.JsonWriterPipeline': 800,
            # 'product.pipelines.pipeline.MongoPipeline': 800,
        },
        'SPIDER_MIDDLEWARES': {
            'product.middlewares.spidermiddlewares.ProductSpiderMiddleware': 10,
        }
    }

    def parse(self, response):
        next_pages = response.xpath("//li/a/@href").extract()
        print "next_pages=", next_pages
        print
        for next_page_url in next_pages:
            if re.match(r'(/wiki/%.*?)', next_page_url):
                print "next_url=", next_page_url
                print "full_url=", response.urljoin(next_page_url)
                print
                yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_item, dont_filter=True)

    def parse_item(self, response):
        sites = response.xpath("//div[@id='content']")
        for site in sites:
            item = ProductItem()
            item["name"] = site.xpath("//h1[@class='firstHeading']/text()").extract_first()
            item["alias"] = []
            item["domain"] = "agency from wiki.mbalib.com"

            link = site.xpath("//a[@class='external free']/text()").extract_first()
            content = site.xpath("//div[@class='headline-2'][1]/following-sibling::*[1]")
            desc = content.xpath("string(.)").extract_first().strip("\n")

            item["props"] = [
                {"name": "link", "value": link},
                {"name": "desc", "value": desc}
            ]

            yield item
        print('successfully parsed ' + str(response))
