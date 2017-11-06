from urllib.parse import urlencode

import selenium
from selenium import webdriver


browser = webdriver.Chrome()
base_url = 'http://weixin.sogou.com/weixin?'
browser.add_cookie({
    'name': 'Cookie',
    'value': 'CXID=FA27D4E2D77B2720F24FCBF279E5AB77; SUV=009D399D7672E5B059C2169EF8CAB375; ad=Dlllllllll2BsTtLlllllVXaeoclllllNXaO7lllllylllllpCxlw@@@@@@@@@@@; SUID=B0E572765B68860A59BF773600004110; IPLOC=CN5101; ABTEST=7|1506759233|v1; weixinIndexVisited=1; SNUID=B22902A8CDCB9423916E9EC1CE66C6EF; JSESSIONID=aaa52pUrTDBFxcJSWvz6v; sct=6; ppinf=5|1507540886|1508750486|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo5OiVFRSU5MCU4MnxjcnQ6MTA6MTUwNzU0MDg4NnxyZWZuaWNrOjk6JUVFJTkwJTgyfHVzZXJpZDo0NDpvOXQybHVNOEFUZ0NjdDhzY1BXa3dzc3hHaU1BQHdlaXhpbi5zb2h1LmNvbXw; pprdig=Clidk01t-aHAbkwKoTBH9r_blYsIhopTL4aZ1hfxmAs_GxUXW9aFIswG1hXR32KfEq0OwhNdGe-959xirym90qetvsM_-K1y-6DFrD8jWS4uniC2ATkgdeOWJcJmModWJNYY-vxReMCRGNZzHG5YYSbimCcP-_6Mbd-9ZJm3-xs; sgid=17-31161375-AVnbP5azPhc3zGFIj860HRs; ppmdig=1507540886000000059cb702a0c63360991297bd6fc70f5c',
})


def get_index(page):
    params = {
        'query': '风景',
        'type': 2,
        'page': page,
        'ie': 'utf8',
    }
    url = base_url + urlencode(params)
    print(url)
    browser.get(url)


if __name__ == '__main__':
    for i in range(1,21):
        get_index(i)