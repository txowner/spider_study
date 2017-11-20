# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from fake_useragent import UserAgent


class JobbolespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    """
    根据现成的库 随机生成 uaer-agent， 一般这种更好
    """
    def __init__(self, crawler):
        self.crawler = crawler
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        # 设置user-agent
        request.headers.setdefault('User-Agent', get_ua())
        # request.dont_filter = True
        # print('------->',spider)
        # print('------->',request)
        # if spider.name == 'lagou':
        #     print('****************')
        # 设置ip 代理
        # request.meta['proxy'] = 'http://221.238.67.231:8081'   # 这样就设置了代理


class RandomUserAgentMiddleware_old(object):
    """
    根据自定义的列表 随机生成 uaer-agent
    """
    def __init__(self, crawler):
        self.crawler = crawler
        # super(RandomUserAgentMiddleware, self).__init__()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def random_useragent(self):
        user_agent_list = self.crawler.settings.get('USER_AGENT_LIST', [])
        n = random.randint(0, len(user_agent_list)-1)
        return user_agent_list[n]

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.random_useragent())
