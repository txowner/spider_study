# -*- coding: utf-8 -*-

# Scrapy settings for JobboleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

# 把项目目录加载到环境变量
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)  # 加载到第一，最先找到， append加载到最后


BOT_NAME = 'JobboleSpider'

SPIDER_MODULES = ['JobboleSpider.spiders']
NEWSPIDER_MODULE = 'JobboleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'JobboleSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True   #这里是定制是否遵守robots.txt文件协议，支持的话会过滤掉很多url，爬虫一般选择不支持
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# import random
# n = random.randint(2,5)
DOWNLOAD_DELAY = 3

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_DOMAIN = 3
# CONCURRENT_REQUESTS_PER_IP = 16
# CONCURRENT_REQUESTS_PER_IP = 2

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'JobboleSpider.middlewares.JobbolespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 数字越小的中间件越靠近引擎，数字越大的中间件越靠近下载器
    # 'JobboleSpider.middlewares.MyCustomDownloaderMiddleware': 543,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  #这是scrapy默认的useragentmiddleware 序号为None，表示禁止该中间件
    # 'JobboleSpider.middlewares.RandomUserAgentMiddleware':200,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #  'JobboleSpider.pipelines.JobbolespiderPipeline': 300,
   #  'JobboleSpider.pipelines.ArticleSaveToMongoDBPipeline': 400,   # 存储到Mongodb
   #  'JobboleSpider.pipelines.MysqlPipeline': 400,   # 以同步的方式存储到mysql
    'JobboleSpider.pipelines.MysqlTwistedPipeline': 600,   # 以异步的方式存储到mysql
   #  'scrapy.contrib.pipeline.images.ImagesPipeline': 500   # scrapy自带的下载图片的pipeline
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# MONGODB 配置
MONGO_URI = 'localhost'
MONGO_DB = 'JobboleArticle'


#存储数据到Mysql 配置
MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'jobbole_spider'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'


# 下载图片设置
IMAGES_URLS_FIELD = 'front_image_url'     # 指定要下载图片的url在item中是哪一个字段，不指定则默认是image_urls
# IMAGES_MIN_WIDTH = 100     # 这里指明要下载的图片的最小宽度和高度
# IMAGES_MIN_HEIGHT = 100
IMAGES_STORE = os.path.join(BASE_DIR, 'images')


# 设置时间格式
SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SQL_DATE_FORMAT = '%Y-%m-%d'


# 设置USER_AGENT
# USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
# USER_AGENT_LIST = [
#     "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
#     "Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00",
#     "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
# ]

# 配置现成user-agent 代理库生成的类型
UA_TYPE = 'random'

# 一个提示，看看开启有什么效果
DUPEFILTER_DEBUG = True