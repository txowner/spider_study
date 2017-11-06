# -*- coding: utf-8 -*-
import scrapy

from quotetutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        quotes = response.css('.quote')
        for quote in quotes:
            item = QuoteItem()

            text = quote.css('.text::text').extract_first()
            author = quote.css('.author::text').extract_first()
            tags = quote.css('.tags .tag::text').extract()

            item['text'] = text
            item['author'] = author
            item['tags'] = tags

            yield item

        # 翻页
        next = response.css('.next a::attr("href")').extract_first()    # /page/2/
        url = response.urljoin(next)     # 把相对路径连接成绝对路径  http://quotes.toscrape.com/page/2/
        yield scrapy.Request(url=url, callback=self.parse)   # 请求下一页，把response返回给callback指定函数继续处理，递归调用自己
