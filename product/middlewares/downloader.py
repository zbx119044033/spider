# -*- coding: utf-8 -*-
# here defined my downloader middleware

import random
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from selenium import webdriver
from scrapy.http import HtmlResponse
import time


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == "gold_pro":
            print "PhantomJS is starting..."
            driver = webdriver.PhantomJS()  # 指定使用的浏览器
            request.meta['driver'] = driver
            # driver = webdriver.Firefox()
            driver.get(request.url)
            time.sleep(1)
            js = "var q=document.documentElement.scrollTop=10000"
            driver.execute_script(js)  # 可执行js，模仿用户操作。此处为将页面拉至最底端。
            time.sleep(1)
            body = driver.page_source
            print ("visiting" + request.url)
            # print body
            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        else:
            return


class IPPool(HttpProxyMiddleware):
    def __init__(self, ip=''):
        super(IPPool, self).__init__()
        self.ip = ip

    def process_request(self, request, spider):
        ip = random.choice(self.ip_pool)
        print 'current IP: ' + ip
        try:
            request.meta["proxy"] = "http://" + ip
        except Exception, e:
            print e
            pass

    def process_response(self, request, response, spider):
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            ip = random.choice(self.ip_pool)
            print 'current IP: ' + ip
            request.meta['proxy'] = "http://" + ip
            return request
        return response

    with open("proxies.txt", "r") as f:
        proxy = f.readlines()
        ip_pool = [ip.strip() for ip in proxy]


class UAPool(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        super(UAPool, self).__init__(user_agent)
        self.user_agent = user_agent

    def process_request(self, request, spider):
        # choose user-agent randomly
        ua = random.choice(self.user_agent_list)
        print 'User-Agent:' + ua
        try:
            request.headers.setdefault('User-Agent', ua)
        except Exception, e:
            print e
        pass

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    ]
