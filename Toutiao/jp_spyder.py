import re
import os, sys
from urllib.parse import urlencode
import pymongo
import requests
import json
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from hashlib import md5
from multiprocessing import Pool

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(BASE_DIR)
from .config import *



def get_page_index(offset, keyword):
    """
    模拟ajax请求keyword索引页源码
    :return: offset的索引页源码
    """
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text       # response.text获取的结果是str类型
        return None
    except RequestException:
        print('请求索引页出错！')
        return None


def parse_page_index(html):
    """
    解析索引页数据，提取每一个详情页的url
    :param html: 
    :return: 
    """
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def get_page_detail(url):
    """
    请求每篇文章(详情页)的内容，返回详情页的源码
    :param url: 
    :return: 
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text       # response.text获取的结果是str类型
        return None
    except RequestException:
        print('请求详情页出错！')
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    pattern = re.compile('BASE_DATA.galleryInfo =.*?gallery:.*?(.*?)siblingList:', re.S)
    result = re.search(pattern, html)
    if result:
        data = json.loads(result.group(1).strip()[:-1])    #这里由于写的正则表达式问题，匹配出来的最后有逗号和空格，要去掉。。。
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for img_url in images:
                download_images(img_url)       # 下载图片

            return {
                'title': title,
                'url': url,
                'images': images,
            }
    else:
        return None


def connect_mongo():
    """
    连接mongodb
    :return: 
    """
    # 建立MongoDB数据库连接 , connect=False 在多进程时可以消除报错, 作用：在每个进程启动时，都单独起一个连接
    client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT, connect=False)
    # 连接所需的数据库，MONGO_DB的值是数据库名
    db = client[MONGO_DB]

    return client, db


def save_data_to_mongo(data):
    """
    存储数据到MongoDB
    :param data: 
    :return: 
    """
    client, db = connect_mongo()
    if db[MONGO_TABLE].insert(data):
        print("存储成功：", data.get('title'))
        return True
    return False


def download_images(url):
    """
    下载图片
    :param url: 
    :return: 
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_images(response.content)  # response.content获取的结果是bytes类型
        return None
    except RequestException:
        print('下载图片出错！')
        return None


def save_images(content):
    # 用MD5加密作用： 如果加密内容一样，那么返回的md5加密值就一样，这样就只有一个图片，不会重复
    file_path = '{0}/{1}.{2}'.format(os.getcwd()+'/images', md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(offset):
    """
    程序入口函数
    :return: 
    """
    html = get_page_index(offset, KEYWORD)
    # print(html)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result:
                save_data_to_mongo(result)


if __name__ == '__main__':
    pool = Pool()
    group = [i*20 for i in range(START, END+1)]
    pool.map(main, group)
    print('存储数据到Mongodb成功')
