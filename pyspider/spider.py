#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-10-10 15:34:13
# Project: tripadvisor

from pyspider.libs.base_handler import *
import pymongo


class Handler(BaseHandler):
    crawl_config = {    # self.crawl的参数配置dic
    }
    
    client = pymongo.MongoClient('localhost')
    db = client['TripAdvisor']


    @every(minutes=24 * 60)   # 每隔多少分钟重新执行这个函数， 若为seconds是每隔多少秒
    def on_start(self):     # 程序入口
        self.crawl('https://www.tripadvisor.cn/Attractions-g186338-Activities-c47-t163-London_England.html#ATTRACTION_LIST', callback=self.index_page)

        
    @config(age=10 * 24 * 60 * 60)      # 过期时间，多少秒， 在过期之前项目将不会再次执行这个函数
    def index_page(self, response):
        for each in response.doc('div > div.listing_info > div.listing_title > a').items():
            self.crawl(each.attr.href, callback=self.detail_page)
        # 获取 ‘下一页’图标 的url
        next = response.doc('.next').attr('href')
        self.crawl(next, callback=self.index_page)
            
            
    @config(priority=2)
    def detail_page(self, response):   # 这些定义好的函数都会自动请求给定的url 
        url = response.url
        title = response.doc('.heading_title').text()
        rating = response.doc('div > .more').text()
        address = response.doc('#taplc_attraction_detail_listing_0 > div.section.location').text()
        phone = response.doc('.headerBL .phone > span').text()
        duration = response.doc('.hours > .duration').text()
        business_time = response.doc('div.detail_section.hours > div:nth-child(2) > div').text()
        
        return {
            "url": url,
            "title": title,
            "rating": rating,
            "address": address,
            "phone": phone,
            "duration": duration,
            "business_time": business_time,
        }

    
    def on_result(self, data):    # pyspider会自动调用，具体啥时候调用？
        # 保存数据到MongoDB
        if data:
            self.save_to_mongo(data)
            

    def save_to_mongo(self, data):
        if self.db['London'].insert(data):
            print('存储到Mongodb成功')
        