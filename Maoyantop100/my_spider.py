import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool


def get_one_page_source(url):
    """
    请求url，返回源码
    :param url: 传入的url
    :return: 成功返回页面源码，否则返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari / 537.36',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    """
    用正则表达式解析源码，提取数据
    :param html:  源码
    :return: 
    """
    pattern = re.compile('<dd>.*?board-index.*?">(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?">(.*?)</a>.*?star">(.*?)'
                         +'</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # print("======",html)   # 下面定义了生成器， 不迭代生成器这里打印没有效果
    for item in items:
        yield {                 # 生成器
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],    # 去掉空白字符，然后去掉‘主演：’ 这三个字符
            'time': item[4].strip()[5:],    # 去掉空白字符，然后去掉‘上映时间：’ 这五个字符
            'score': item[5]+item[6]
        }


def write_to_file(content):
    with open('result.txt', 'a', encoding='utf8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')   # 要存储中文， 这两个都不能少


def main(offset):
    """
    :param url:  传入的url
    :return: 
    """
    url = "http://maoyan.com/board/4?offset=" + str(offset)
    html = get_one_page_source(url)
    if html:
        for item in parse_one_page(html):
            write_to_file(item)
    else:
        print('requests error!')


if __name__ == '__main__':
    # for i in range(10):
    #     main(i*10)
    pool = Pool()   # 实例化一个进程池, 如果进程池还有剩余，当有新任务时，就会新开一个进程去处理这个新任务
    pool.map(main, [i*10 for i in range(10)])