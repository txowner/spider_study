# -*- coding: utf-8 -*-
from urllib.parse import urljoin
import scrapy

from items import JobboleArticleItem, JobboleArticleItemLoader
from utils.common import get_md5


class JobloleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1、选择索引页每篇文章的url以及封面图url
        2、找到下一页的链接
        :param response: 
        :return: 
        """
        # 获取索引页面中详情页的url、每个详情页的封面图的url
        post_nodes = response.css('.post.floated-thumb .post-thumb a')
        for node in post_nodes:
            detail_url = node.css('::attr(href)').extract_first()
            front_image_url = node.css('img::attr(src)').extract_first()
            # 由于有点封面图是相对路径，有的是绝对路径，处理如下：
            front_img_url = urljoin(response.url, front_image_url)   # 若之前的front_img_url有域名，则覆盖前面的，否则连接前面的域名

            # 生成新的Request请求对象，用yield返回给调度器, 用meta给灰调函数的response传递值
            yield scrapy.Request(url=detail_url, meta={'front_image_url': front_image_url}, callback=self.parse_detail, dont_filter=True)

        # 获取下一页链接
        next_page_url = response.css('.next ::attr(href)').extract_first('')
        if next_page_url:
            yield scrapy.Request(url=next_page_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        1、解析下载的详情页源码，从中提取数据
        :param response: 
        :return: 
        """
        # 利用基础的item实现的item
        # url = response.url
        # url_object_id = get_md5(response.url)
        # front_image_url = response.meta.get('front_image_url', '')
        # title = response.css('.entry-header h1::text').extract_first('')
        # create_data = response.css('.entry-meta-hide-on-mobile::text').re('.*?((\d{4})/(\d{1,2})/(\d{1,2})).*')[0]
        #
        # tags_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tags = '·'.join([tag for tag in tags_list if "评论" not in tag])
        #
        # thumbs_up = int(response.css('.vote-post-up h10::text').extract_first(0))
        #
        # collected = response.css('.bookmark-btn::text').re('(\d+)')
        # collected = collected[0] if collected else 0
        #
        # comments = response.css('.post-adds a span::text').re('.*?(\d+).*')
        # comments = comments[0] if comments else 0
        #
        # content = response.css('.entry').extract_first('')
        #
        # JobboleItem = JobboleArticleItem()
        #
        # JobboleItem['url'] = url
        # JobboleItem['url_object_id'] = url_object_id
        # JobboleItem['front_image_url'] = [front_image_url]    # 用scrapy自带的imagepipeline下载图片时，是循环获取图片链接。所以这里必须是可循环的对象
        # JobboleItem['title'] = title
        # JobboleItem['create_data'] = create_data
        # JobboleItem['tags'] = tags
        # JobboleItem['thumbs_up'] = thumbs_up
        # JobboleItem['collected'] = collected
        # JobboleItem['comments'] = comments
        # JobboleItem['content'] = content
        #
        # yield JobboleItem


        # 使用 Item Loader 加载item
        item_loader = JobboleArticleItemLoader(item=JobboleArticleItem(), response=response)   # 生成一个item loader 对象

        # 常用的添加规则的方法： add_css, add_xpath  直接添加值的方法： add_value

        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('front_image_url', response.meta.get('front_image_url', ''))
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_data', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('thumbs_up', '.vote-post-up h10::text')
        item_loader.add_css('collected', '.bookmark-btn::text')
        item_loader.add_css('comments', '.post-adds a span::text')
        item_loader.add_css('content', '.entry')

        # 在添加完规则之后，要调用一下item_loader的load_item方法
        article_item = item_loader.load_item()

        yield article_item


