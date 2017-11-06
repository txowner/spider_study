# -*- coding: utf-8 -*-
import datetime
import re
import json
import time
from urllib.parse import urljoin
import scrapy

# 这里在settings里面加载了root路径的，shell里面正常运行，显示问题
from items import ZhihuQuestionItem, ZhihuAnswersItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # 没个问题的评论是请求接口，由ajax返回
    start_answers_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'

    login_url = 'https://www.zhihu.com/#signin'
    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    }

    # 一般scrapy 默认的请求入口是 start_requests , 但是由于知乎是要先登录的，所以这里我们 需要重写入口方法
    def start_requests(self):
        """
        1、重写scrapy入口函数，先实现用户登录
        2、获取验证码图片
        :return: 
        """
        # 这里获取验证码
        t = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
        yield scrapy.Request(url=captcha_url, headers=self.headers, callback=self.get_captcha)

    def get_captcha(self, response):
        """
        1、获取验证码图片，并保存，让用户识别 输入
        2、获取 _xsef code
        3、吧验证码和_xsrf 传入fromdata
        :param response: 
        :return: 
        """
        with open("utils/captcha.jpg", "wb") as f:
            f.write(response.body)

        from PIL import Image
        try:
            # 这里是pillow库的一个小bug，记住了，要这样写
            with open('utils/captcha.jpg', 'rb') as im_handle:
                im = Image.open(im_handle)
                im.show()
        except:
            print("===============")

        captcha = input("输入验证码:\n>")

        # 这里 获取 _xsrf code
        yield scrapy.Request(url=self.login_url, headers=self.headers, meta={'captcha': captcha or ''}, callback=self.login)

    def login(self, response):
        """
        从response中提取_xsrf code， 添加到fromdata，发送给登录页面
        :param response: 
        :return: 
        """
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.S)
        if match_obj:
            xsrf = match_obj.group(1)
        else:
            xsrf = ""

        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": '13281826916',
                "password": 'tianxu7098++',
                "captcha": response.meta.get('captcha', '')
            }
            yield scrapy.FormRequest(url=post_url, formdata=post_data, headers=self.headers, callback=self.check_login)

    def check_login(self, response):
        """
        验证服务器返回的数据，判断是否登录成功
        :param response: 
        :return: 
        """
        test_json = json.loads(response.text)
        # with open('index.html', 'wb') as f:
        #     f.write(response.text.encode('utf8'))
        if 'msg' in test_json and test_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url=url, headers=self.headers, dont_filter=True, callback=self.parse)   # 不写回调函数，默认是self.parse

    def parse(self, response):
        """
        1、到这个函数，说明登录成功了
        2、这个页面主要就是问答，把所有a标签中的链接取出来，过滤掉加载js等链接，再找出具有questions的链接
        :param response: 
        :return: 
        """
        # 获取当前页面的所有链接
        all_urls = response.css('a::attr(href)').extract()

        # 有的页面中，问题的url是相对url，此时需要加上啊域名
        dealed_url = set()
        for url in all_urls:
            if url.startswith('/'):
                dealed_url.add(urljoin('https://www.zhihu.com', url))

        # 过滤掉加载js等没用的链接, filter是把可迭代对象中的每一项当作参数传递给前面这个函数，并返回一个迭代器
        all_urls = filter(lambda x: True if x.startswith('https') else False, dealed_url)

        # 过滤出问题(带有questions的)链接
        for url in all_urls:
            match_obj = re.match('(.*?zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                url = match_obj.group(1)
                zhihu_id = match_obj.group(2)
                # 这里说明当前url就是带有questions的url，即我们需要的url， 下面就将这个url生成Request对象，发送给调度器
                yield scrapy.Request(url=url, headers=self.headers, meta={'zhihu_id': zhihu_id}, callback=self.parse_questions)

            else:
                # 说明当前url不是带有questions的url，我们可以再次请求，再解析页面中的url，即：重复执行这个函数
                # yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)
                pass
                # 若这里注释 是 为了在调试时 少向知乎发起请求

    def parse_questions(self, response):
        """
        解析某个 ‘问题’ 页面，提取数据，收集到item
        :param response: 
        :return: 
        """
        zhihu_question_item = ZhihuQuestionItem()

        # 从response中提取出想要的信息
        url = response.url
        zhihu_id = response.meta.get('zhihu_id')
        topic = ','.join(response.css('.QuestionHeader-topics .Popover div::text').extract())
        title = response.css('.QuestionHeader h1.QuestionHeader-title::text').extract_first('')
        content = response.css('.QuestionRichText span::text').extract_first('')
        answer_num = int(response.css('.List-headerText span::text').extract_first(0))
        comments_num = int(response.css('.QuestionHeader-Comment button::text').re('(\d+)')[0])
        watch_user_num = int(response.css('.NumberBoard-value::text').re('(\d+)')[0])
        click_num = int(response.css('.NumberBoard-value::text').re('(\d+)')[1])

        # 把上面提取出来的信息填充到 item 中
        zhihu_question_item['url'] = url
        zhihu_question_item['zhihu_id'] = zhihu_id
        zhihu_question_item['topic'] = topic
        zhihu_question_item['title'] = title
        zhihu_question_item['content'] = content
        zhihu_question_item['answer_num'] = answer_num
        zhihu_question_item['comments_num'] = comments_num
        zhihu_question_item['watch_user_num'] = watch_user_num
        zhihu_question_item['click_num'] = click_num

        # 到这里还要解析问题的回答信息，在这里触发第问题答案的初始请求，offset为0
        yield scrapy.Request(url=self.start_answers_url.format(zhihu_id, 20, 0), headers=self.headers, callback=self.parse_answers)

        # 用yield 把 item 传输到pipeline
        yield zhihu_question_item
        #  注释是因为，几个爬虫返回去到pipeline里面的都叫item，如何区分？

        # 按理说爬取全站，是每个页面的所有url都应该提取出来，做self.parse里面的操做，这里为了简化代码，提高可读性，暂时不做，可以最后加
        """
        # 获取当前页面的所有链接
        all_urls = response.css('a::attr(href)').extract()

        # 有的页面中，问题的url是相对url，此时需要加上啊域名
        dealed_url = set()
        for url in all_urls:
            if url.startswith('/'):
                dealed_url.add(urljoin('https://www.zhihu.com', url))

        # 过滤掉加载js等没用的链接, filter是把可迭代对象中的每一项当作参数传递给前面这个函数，并返回一个迭代器
        all_urls1 = filter(lambda x: True if x.startswith('https') else False, dealed_url)

        # 过滤出问题(带有questions的)链接
        for url in all_urls1:
            match_obj = re.match('(.*?zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                url = match_obj.group(1)
                zhihu_id = match_obj.group(2)
                # 这里说明当前url就是带有questions的url，即我们需要的url， 下面就将这个url生成Request对象，发送给调度器
                yield scrapy.Request(url=url, headers=self.headers, meta={'zhihu_id': zhihu_id},
                                     callback=self.parse_questions)

            else:
                # 说明当前url不是带有questions的url，我们可以再次请求，再解析页面中的url，即：重复执行这个函数
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)
                # 若这里注释 是 为了在调试时 少向知乎发起请求
        """

    def parse_answers(self, response):
        """
        问题的回答是接口请求的， 所以这里返回的是类似于字典的json格式化数据，直接json.loads后，字典操作来提取
        :param response: 
        :return: 
        """
        # 把 返回来的json数据 loads成 python的字典对象
        json_ans = json.loads(response.text)

        # 从接口返回数据中提取需要的数据
        if 'data' in json_ans.keys():
            for answer in json_ans['data']:
                # 提取的 一组数据就要返回一个item， 所以这里放在循环内部
                zhihu_answers_item = ZhihuAnswersItem()

                zhihu_answers_item['url'] = answer.get('url')
                zhihu_answers_item['answer_id'] = answer.get('id', None)
                zhihu_answers_item['question_id'] = answer['question'].get('id', None)
                zhihu_answers_item['author_id'] = answer['author'].get('id')
                zhihu_answers_item['content'] = answer.get('content') or answer.get('excerpt')
                zhihu_answers_item['praise_num'] = answer.get('voteup_count', 0)
                zhihu_answers_item['comments_num'] = answer.get('comment_count', 0)
                zhihu_answers_item['create_time'] = answer.get('created_time')
                zhihu_answers_item['update_time'] = answer.get('updated_time')
                zhihu_answers_item['crawl_time'] = datetime.datetime.now()

                # 用yield 传送到pipeline, scrapy是基于深度优先遍历， 这里由yield体现
                yield zhihu_answers_item

        # 判断是否是最后一页，不是的话，就获取下一页，生成Request
        if 'paging' in json_ans.keys():
            if not json_ans['paging'].get('is_end'):
                next = json_ans['paging'].get('next')
                yield scrapy.Request(url=next, headers=self.headers, callback=self.parse_answers)

