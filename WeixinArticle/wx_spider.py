from urllib.parse import urlencode

import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq


base_url = 'http://weixin.sogou.com/weixin?'
KEYWORD = '风景'
PROXY_URL = 'http://127.0.0.1:5000/get'
MAX_COUNT = 5

headers = {
    'Cookie': 'CXID=FA27D4E2D77B2720F24FCBF279E5AB77; SUV=009D399D7672E5B059C2169EF8CAB375; ad=Dlllllllll2BsTtLlllllVXaeoclllllNXaO7lllllylllllpCxlw@@@@@@@@@@@; SUID=B0E572765B68860A59BF773600004110; IPLOC=CN5101; ABTEST=7|1506759233|v1; weixinIndexVisited=1; SNUID=B22902A8CDCB9423916E9EC1CE66C6EF; JSESSIONID=aaa52pUrTDBFxcJSWvz6v; sct=6; ppinf=5|1507540886|1508750486|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo5OiVFRSU5MCU4MnxjcnQ6MTA6MTUwNzU0MDg4NnxyZWZuaWNrOjk6JUVFJTkwJTgyfHVzZXJpZDo0NDpvOXQybHVNOEFUZ0NjdDhzY1BXa3dzc3hHaU1BQHdlaXhpbi5zb2h1LmNvbXw; pprdig=Clidk01t-aHAbkwKoTBH9r_blYsIhopTL4aZ1hfxmAs_GxUXW9aFIswG1hXR32KfEq0OwhNdGe-959xirym90qetvsM_-K1y-6DFrD8jWS4uniC2ATkgdeOWJcJmModWJNYY-vxReMCRGNZzHG5YYSbimCcP-_6Mbd-9ZJm3-xs; sgid=17-31161375-AVnbP5azPhc3zGFIj860HRs; ppmdig=1507540886000000059cb702a0c63360991297bd6fc70f5c',
    'Host': 'weixin.sogou.com',
    'Referer': 'http://weixin.sogou.com/weixin?query=%E9%A3%8E%E6%99%AF&type=2&page=1&ie=utf8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
}

proxy = None


def get_index(KEYWORD, page, count=0):
    global proxy
    params = {
        'query': KEYWORD,
        'type': 2,
        'page': page,
        'ie': 'utf8',
    }
    url = base_url + urlencode(params)
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, headers=headers)
        if 'IP:' in response.text:
            print('被封IP了～')
            # 切换代理
            proxy = get_proxy(PROXY_URL)
            if proxy:
                print('Using proxy success', proxy)
                get_index(KEYWORD, page)
            else:
                print('Using proxy failed', proxy)
                return None
        else:
            return response.text

    except RequestException:
        print('repeat')
        count += 1
        if count <= MAX_COUNT:
            get_index(KEYWORD, page, count)


def parse_index(html):
    if html:
        doc = pq(html)
        items = doc('.new_list li .txt-box h3 a').items()
        for item in items:
            yield item.attr('href')


def get_proxy(proxy_url):
    try:
        response = requests.get(proxy_url)
        if response.status_code == 200:
            return response.text
        return None

    except  RequestException:
        get_proxy(proxy_url)


if __name__ == '__main__':
    for i in range(1,101):
        print(i)
        html = get_index(KEYWORD, i)
        print(html)
        for url in parse_index(html):
            print("=========", url)