# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# pipeline 是对item的进一步筛选，处理。 在这里定义pipeline后要在settings里面去注册，并指定优先级
import pymongo
from scrapy.exceptions import DropItem


class TextPipeline(object):
    """
    处理item中text的pipeline
    """
    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):
        """
        注意： 一个处理item的pipeline 必须实现 process_item 这个方法 且必须返回item 或者 DropItem
        :param item: 
        :param spider: 
        :return: 
        """
        if item['text']:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')


class MongoPipeline(object):
    """
    连接MongoDB 并把item存储到MongoDB
    """
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """
        返回MongoPipeline的一个对象，初始值就是settings里面设置的值（这就是在类里面最简单的一个初始化操做，给成员变量赋值）
        :param crawler: 
        :return: 
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        """
        爬虫启动时的相关操作，这里实现 连接mongodb对象
        :param spider: 
        :return: 
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        """
        吧item存储到mongodb
        :param item: 
        :param spider: 
        :return: 
        """
        name = item.__class__.__name__    # 这里的name获取的是item对应的类名
        self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        """
        关闭mongodb连接
        :param spider: 
        :return: 
        """
        self.client.close()