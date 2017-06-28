# Spider
Here stores my own spider based on python 2.7.14

# Dependency
scrapy 1.4.0

# Description
The spiders in this package are used to crawl propertities on insurance product from cngold.com/vobao.com/mbalib.com and so on

The data structure is defined in items.py

The middlewares defines the downloader middlewares such as javascript middlewares to simulate user operation via PhantomJS, the UAPool to change user-agent randomly, the IPPool to change IP randomly. The spider middleware defined the spider operation rules.

The piplines defined the FilterPipeline to filter data from raw data, the JsonWriter to dump data into json formate, the MongoPipeline to insert data into MongoDB.

The spiders defined all of my own spiders to extract data from original website.

# Reference
scrapy docs: http://scrapy-chs.readthedocs.io/zh_CN/1.0/intro/overview.html
