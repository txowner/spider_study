# -*- coding: utf-8 -*-
import json
import scrapy
import sys

print(sys.path)
from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'

    # 用户个人主页
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_include = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 用户的关注列表(人)
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&limit=20&offset={offset}'
    followees_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    # 用户关注的人
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&limit=20&offset={offset}'
    followers_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield scrapy.Request(url=self.user_url.format(user=self.start_user, include=self.user_include), callback=self.parse_user)
        yield scrapy.Request(url=self.followees_url.format(user=self.start_user, include=self.followees_include, offset=0), callback=self.parse_followees)
        yield scrapy.Request(url=self.followers_url.format(user=self.start_user, include=self.followers_include, offset=0), callback=self.parse_followers)

    def parse_user(self, response):
        results = json.loads(response.text)
        item = UserItem()
        for field in item.fields:     # item.fields 属性： 把item中的字段以集合形式返回
            if field in results.keys():
                item[field] = results.get(field)

        yield item  # 用yield把item返回，此时这个item就可以直接进行pipeline等操做

        # 这里开始递归爬取每个解析出来的用户所关注的人和关注他的人
        # 获取解析出来的每个人的关注列表
        yield scrapy.Request(url=self.followees_url.format(user=results.get('url_token'), include=self.followees_include, offset=0), callback=self.parse_followees)
        # 获取解析出来的每个人关注的人的列表
        yield scrapy.Request(url=self.followers_url.format(user=results.get('url_token'), include=self.followers_include, offset=0), callback=self.parse_followers)

    def parse_followees(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for user_obj in results.get('data'):
                yield scrapy.Request(url=self.user_url.format(user=user_obj.get('url_token'), include=self.user_include), callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse_followees)   # 这里的yield会直接把后面的Request交给scapy的下载器


    def parse_followers(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for user_obj in results.get('data'):
                yield scrapy.Request(
                    url=self.user_url.format(user=user_obj.get('url_token'), include=self.user_include),
                    callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse_followers)   # 这里的yield会直接把后面的Request交给scapy的下载器