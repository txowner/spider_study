# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import MySQLdb
import MySQLdb.cursors
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class JobbolespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleSaveToMongoDBPipeline(object):
    """
    将接收到的item数据集保存到MongoDB
    """

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    # 目前感觉用起来和from_crawler效果一样
    @classmethod
    def from_settings(cls, settings):
        mongo_uri = settings["MONGO_URI"]
        mongo_db = settings["MONGO_DB"]
        return cls(mongo_uri, mongo_db)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        # self.db[collection_name].insert(dict(item))   # 这里直接插入不好，为防止重复，用update更好，没有就插入，有就更新
        self.db[collection_name].update({'url_object_id': item['url_object_id']}, {'$set': item}, True)
        # update 第一个参数是判断条件，是否存在， 第二个参数是要更新的item，键名固定， 第三个参数为True表示存在就更新，不存在就插入

        return item


class MysqlPipeline(object):
    """
    采用同步的方式将数据保存到mysql
    由于scrapy基于Twisted异步网络框架，会存在存入mysql的速度远远低于item数据到pipeline的速度，会造成数据丢失严重
    """
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'root', 'jobbole_spider', charset='utf8', use_unicode=True)
        # 其中 use_unicode 在python3默认是True， 在python2是False
        self.cursor = self.conn.cursor()   # 定义游标

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(url, url_object_id, front_image_url, title, create_data, tags, thumbs_up, 
            collected, comments, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        """
        self.cursor.execute(insert_sql, (item['url'],item['url_object_id'],item['front_image_url'][0],item['title'],
            item['create_data'],item['tags'],item['thumbs_up'],item['collected'],item['comments'],item['content']
        ))
        self.conn.commit()   # 一定要记得commit，眨眼才能吧数据提交到Mysql


class MysqlTwistedPipeline(object):
    """
    以异步的方式把数据存入mysql
    下面绝大部分代码都是固定的，每次更换项目字需要修改一点代码即可(插入数据的sql语句，现在放在每个item中去了，也就是这边可以直接利用)
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)   # 生成一个数据库连接池，第一个参数为采用什么API，第二个参数为连接信息

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)   # runInteraction 吧传入的函数变成异步操作
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)
        """
        (1062, "Duplicate entry '41233373' for key 'PRIMARY'") 这是说明主键冲突了(插入了重复数据)
        解决： 在插入的sql语句加上验证： 不存在就插入，存在就更新， 实现见每条插入sql语句
        """

    def do_insert(self, cursor, item):
        # 获取不同item自带的get_insert_sql返回的sql语句，执行插入操做
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

    '''
    def do_insert(self, cursor, item):
        # 执行具体的插入， cursor是在 runInteraction 异步时自动传进去的可异步的游标
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        if item.__class__ == 'ZhihuQuestionItem':
            insert_sql = """
                           insert into jobbole_article(url, url_object_id, front_image_url, title, create_data, tags, thumbs_up, 
                           collected, comments, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                       """
            cursor.execute(insert_sql, (item['url'], item['url_object_id'], item['front_image_url'][0], item['title'],
                                        item['create_data'], item['tags'], item['thumbs_up'], item['collected'],
                                        item['comments'], item['content']
                                        ))
            # 这里不用再commit，会自动commit
        elif item.__class__ == 'ZhihuAnswersItem':
            # ...
            pass
    '''

class JsonExporterPipleline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# class ArticleImagePipeline(ImagesPipeline):
#     """
#     继承并重载下载封面图的Pipeline的部分功能
#     """
#     def item_completed(self, results, item, info):
#         if "front_image_url" in item:
#             image_file_path = ''
#             for ok, value in results:
#                 image_file_path = value["path"]
#             item["front_image_path"] = image_file_path
#
#         return item