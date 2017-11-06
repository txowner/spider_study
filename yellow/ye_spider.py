import os
import re
from hashlib import md5
import requests
from requests.exceptions import RequestException


def get_index_page(s, url):
    """
    获取网页的源码
    :param s: 保存的会话对象 
    :param url:    目标url 
    :return: 正常返回网页源码  错误返回None
    """
    try:
        response = s.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        get_index_page(s, url)


def parse_index_page(html):
    """
    解析网页内容
    :param html: 源码
    :return: 
    """
    pattern = re.compile('<tbody.*?normalthread.*?">.*?<a.*?"></a>.*?<a.*?href="(.*?)".*?">(.*?)</a>.*?</tbody>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'url': item[0],
            'title': item[1],
        }


def get_page_detail(s, url):
    """
    获取详情页信息
    :param s: 保存的会话对象 
    :param url: 请求的url
    :return: 返回详情页源码
    """
    try:
        response = s.get(url)
        if response.status_code == 200:
            # print(response.text)
            return response.text
        return None
    except RequestException:
        get_index_page(s, url)


def parse_page_detail(html):
    """
    解析详情页源码
    :param html:   详情页源码 
    :return: 一个个图片链接
    """
    pattern = re.compile('<ignore_js_op.*?<img.*?zoomfile="(.*?)".*?</ignore_js_op>', re.S)
    images_url = re.findall(pattern, html)
    # print(images_url)
    for img_url in images_url:
        yield {
            'img_url': img_url,
        }


def download_image(s, url):
    """
    下载图片
    :param s: 保存的会话对象 
    :param url: 
    :return: 
    """
    print('正在下载：',url)
    try:
        response = s.get(url)
        if response.status_code == 200:
            save_image(response.content)
            return None
        return None
    except RequestException:
        download_image(s, url)


def save_image(content):
    """
    保存图片
    :param content: 
    :return: 
    """
    print('正在保存...')
    file_path = '%s/%s.%s' %(os.getcwd()+'/images', md5(content).hexdigest(), 'gif')   # 去重
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main():
    """
    程序入口
    :return: 
    """
    base_url = 'http://www.yousowet.cc/'
    url = base_url + 'forum-47-1.html'
    login_url = base_url + 'member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LhWQJ&inajax=1'
    formdata = {
        'formhash':77809606,
        'referer':'http://www.yousowet.cc/plugin.php?id=dsu_pauls ign:sign',
        'loginfield':'username',
        'username':'qwerwsx',
        'password':'qwerwsx',
        'questionid':0,
        'answer':''
    }
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.yousowet.cc',
        'Upgrade-Insecure-Requests':1,
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
    }
    s = requests.Session()
    s.get('http://www.yousowet.cc/data/cache/ajax.js?P5D')
    s.post(login_url, formdata, headers)
    resp = s.get('http://www.yousowet.cc/thread-2381-1-1.html')
    # print('text:', resp.text)

    html = get_index_page(s, url)
    if html:
        for item in parse_index_page(html):
            detail_page_url = base_url + item['url']
            html = get_page_detail(s, detail_page_url)
            for url_dic in parse_page_detail(html):
                img_url = base_url + url_dic['img_url']
                download_image(s, img_url)


if __name__ == '__main__':
    main()


