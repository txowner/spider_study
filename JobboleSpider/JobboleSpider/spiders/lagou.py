# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LagoujobItem, LagoujobItemLoader
from utils.common import get_md5
from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=('jobs/\d+.html$',)), follow=True),    # 这里的allow可以是元组（可以一个或多个正则表达式），也可以是字符串
        Rule(LinkExtractor(allow=('zhaopin/.*',)), follow=True),       # follow=True 表示如果当前页面有符合这个规则的，就继续提取爬行
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html$'), callback='parse_job', follow=True),
    )
    #
    # def _build_request(self, rule, link):
    #     r = scrapy.Request(url=link.url, callback=self._response_downloaded, dont_filter=True)
    #     r.meta.update(rule=rule, link_text=link.text)
    #     return r

    def parse_job(self, response):
        """
        提取数据，填充到itemloader
        :param response: 
        :return: 
        """
        # 实例化一个 ItemLoader 对象, 注意，下面是传递的item对象，不是类
        job_itemloader = LagoujobItemLoader(item=LagoujobItem(), response=response)

        # 提取数据
        job_itemloader.add_value('url', response.url)
        job_itemloader.add_value('url_object_id', get_md5(response.url))
        job_itemloader.add_css('title', '.job-name::attr(title)')
        job_itemloader.add_css('salary_min', '.job_request .salary::text')
        job_itemloader.add_css('salary_max', '.job_request .salary::text')
        job_itemloader.add_css('work_years_min', '.job_request span::text')
        job_itemloader.add_css('work_years_max', '.job_request span::text')
        job_itemloader.add_css('job_city', '.job_request span::text')
        job_itemloader.add_css('job_type', '.job_request span::text')
        job_itemloader.add_css('degree_need', '.job_request span::text')
        job_itemloader.add_css('publish_time', '.publish_time::text')
        job_itemloader.add_css('tags', '.position-label li::text')
        job_itemloader.add_css('job_advantage', '.job-advantage p::text')
        job_itemloader.add_css('job_descript', '.job_bt div')      # 这里保存内容时，最好连着html一起保存， 后面查询的时候好用
        job_itemloader.add_css('job_address', '.work_addr a::text')
        job_itemloader.add_css('company_name', '#job_company a img::attr(alt)')
        job_itemloader.add_css('company_url', '#job_company a::attr(href)')
        job_itemloader.add_value('crawl_time', datetime.now())

        job_itemloader.load_item()

        return job_itemloader
