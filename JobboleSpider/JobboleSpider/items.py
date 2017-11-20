# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import re
import datetime
from settings import SQL_DATETIME_FORMAT



class JobbolespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

#
# class JobboleArticleItem(scrapy.Item):
    # 搭配基础的item提取数据方式
    # url = scrapy.Field()
    # url_object_id = scrapy.Field()
    # front_image_url = scrapy.Field()
    # title = scrapy.Field()
    # create_data = scrapy.Field()
    # tags = scrapy.Field()
    # thumbs_up = scrapy.Field()
    # collected = scrapy.Field()
    # comments = scrapy.Field()
    # content = scrapy.Field()


class JobboleArticleItemLoader(ItemLoader):
    # 自定义item loader
    default_output_processor = TakeFirst()


# 配合item loader字段处理的函数,  这些函数的参数都是item loader收集起来的item对应字段列表里面的每个元素,自己会循环
def return_value(value):
    return value

def date_convert(value):
    parttern = re.compile('.*?((\d{4})/(\d{1,2})/(\d{1,2})).*')
    # parttern = re.compile('.*?((\d+)/(\d+)/(\d+)).*')
    results = re.findall(parttern, value)
    if results:
        return results[0]
    else:
        return datetime.datetime.now().date()


def deal_tags(value):
    # tags = [tag for tag in tags_list if "评论" not in tag]
    if "评论" in value:
        return ""
    else:
        return value


def get_num(value):
    parttern = re.compile('.*?(\d+).*')
    result = re.findall(parttern, value)
    if result:
        return int(result[0])
    else:
        return 0


class JobboleArticleItem(scrapy.Item):
    # 搭配item loader 提取数据方式
    # 注意： 这里传递给MapCompose中函数的参数是这个字段在item loader手机的item列表中的每一项(字符串、数字等)，不是整个列表
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    title = scrapy.Field()
    create_data = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(deal_tags),
        output_processor=Join('·')   # 这里会覆盖上面的default_output_processor
    )
    thumbs_up = scrapy.Field()
    collected = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    comments = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    content = scrapy.Field()

    """
        因为在pipeline里面处理item的时候，不方便区分到底是那个item(可以根据每个item名判断，那样耦合性更高，如果改了item名，
        同时要修改那边关联的地方)，所以最好的办法是把每个插入方法写到item定义里面来，然后在插入时调用item对象自己的插入方法,
        这样就把每个item区分开了。 ON DUPLICATE KEY UPDATE 作用是： 不存在就插入，存在就把后面指定的字段更新
        """

    def get_insert_sql(self):
        # 执行具体的插入， cursor是在 runInteraction 异步时自动传进去的可异步的游标
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql = """
              insert into jobbole_article(url, url_object_id, front_image_url, title, create_data, tags, 
              thumbs_up, collected, comments, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              ON DUPLICATE KEY UPDATE thumbs_up=VALUES(thumbs_up), collected=VALUES(collected), 
              comments=VALUES(comments),content=VALUES(content)
        """
        # 这里要把item换成self，self表示的是item实例化的对象，调用这里时，就是存储了数据的item
        params = (self['url'], self['url_object_id'], self['front_image_url'][0], self['title'], self['create_data'],
                  self['tags'], self['thumbs_up'], self['collected'], self['comments'], self['content']
                  )

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    """
    收集 知乎 问题页面的信息 的item
    """
    url = scrapy.Field()
    zhihu_id = scrapy.Field()
    topic = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    """
    因为在pipeline里面处理item的时候，不方便区分到底是那个item(可以根据每个item名判断，那样耦合性更高，如果改了item名，
    同时要修改那边关联的地方)，所以最好的办法是把每个插入方法写到item定义里面来，然后在插入时调用item对象自己的插入方法,
    这样就把每个item区分开了。
    """

    def get_insert_sql(self):
        # 执行具体的插入， cursor是在 runInteraction 异步时自动传进去的可异步的游标
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql = """
              insert into zhihu_questions(url, zhihu_id, topic, title, content, answer_num, comments_num, 
              watch_user_num, click_num, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), 
              comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num),
              crawl_update_time=VALUES(crawl_time)
        """
        # 这里要把item换成self，self表示的是item实例化的对象，调用这里时，就是存储了数据的item
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (self['url'], self['zhihu_id'], self['topic'], self['title'],self['content'],self['answer_num'],
                  self['comments_num'], self['watch_user_num'], self['click_num'], crawl_time
        )

        return insert_sql, params


class ZhihuAnswersItem(scrapy.Item):
    """
    收集 每个问题的回答信息的item
    """
    url = scrapy.Field()
    answer_id = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 执行具体的插入， cursor是在 runInteraction 异步时自动传进去的可异步的游标
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql = """
              insert into zhihu_answer(url, answer_id, question_id, author_id, content, praise_num, 
              comments_num, create_time, update_time, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(content), praise_num=VALUES(praise_num), 
              comments_num=VALUES(comments_num),update_time=VALUES(update_time),
              crawl_update_time=VALUES(crawl_time)
        """
        # 这里要把item换成self，self表示的是item实例化的对象，调用这里时，就是存储了数据的item
        # 这里的create_time 与update_time 是时间戳，int类型的，我们在数据库存储的是data类型，所以要转换为date类型
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (self['url'], self['answer_id'], self['question_id'], self['author_id'],self['content'],
                  self['praise_num'], self['comments_num'], create_time, update_time, crawl_time
        )

        return insert_sql, params


class LagoujobItemLoader(ItemLoader):
    pass


class LagoujobItem(scrapy.Item):
    """
    手机拉勾网职位item
    """
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    work_years_min = scrapy.Field()
    work_years_max = scrapy.Field()
    job_city = scrapy.Field()
    job_type = scrapy.Field()
    degree_need = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_descript = scrapy.Field()
    job_address = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
