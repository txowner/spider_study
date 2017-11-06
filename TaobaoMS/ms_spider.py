import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *       # 同级目录找不到包的时候， 用 . 就ok
import pymongo

# 连接 mongodb
client = pymongo.MongoClient(MONGO_HOST)
db = client[MONGO_DB]   # 指定数据库

# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
browser = webdriver.Chrome()
# browser.set_window_size(1400, 900)   # 由于phantomjs没有界面， 这里必须设置大小 chrome这些就不用了

# 这里需要判断加载成功后，再进行下一步操做, 所以实例化一个wait
wait = WebDriverWait(browser, 10)   # 实例化一个浏览器等待对象，设置最大超时 10s


def search():
    """
    打开淘宝，搜索 关键字  
    :return: 总页码数
    """
    print('正在搜索...')
    try:
        browser.get('https://www.taobao.com')

        # 选择输入框 这个元素
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))   # 等待查找到的这个元素加载完成才返回这个元素

        # 选择提交按钮
        # input.send_keys(Keys.ENTER)  #这个是发送 ENTER 键
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')
        ))

        # 提交数据
        input.send_keys(KEYWORD)   # 往搜索框 填写数据
        submit.click()    # 点击上面找到的 提交按钮

        # 总的页码数
        total_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')
        ))
        get_products()   # 解析第一页商品信息
        return total_element

    except TimeoutException:
        search()   # 如果出错， 重复操作


def switch_to_page(page_number):
    """
    选择跳到那一页，这里主要是一直循环到下一页
    :param page_number: 跳转到的页码
    :return: 
    """
    print('正在翻页...')
    try:
        input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')
        ))
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')
        ))
        input.clear()   # 清空页码输入框 里面的数据
        input.send_keys(page_number)
        submit.click()

        # 判断是否跳转到指定页码: 找到分页中的active， 判断page_number是否在里面, 如果里面不存在，返回false， 存在 返回‘消息’
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)
        ))
        get_products()   # 解析当前页商品信息

    except TimeoutException:
        switch_to_page(page_number)


def get_products():
    """
    获取每一页的所有商品
    :return: 
    """
    print('正在解析...')
    html = browser.page_source
    doc = pq(html)
    items = doc.items('#mainsrp-itemlist .items .item')
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(data):
    """
    把数据保存到MongoDB
    :param data: 
    :return: 
    """
    try:
        table = db[KEYWORD_TABLE[KEYWORD]]
        if data and table.insert(data):
            print('存储到MongoDB成功')
    except Exception:
        print("存储到MongoDB失败")


def main():
    """
    程序入口
    :return: 
    """
    try:
        total_element = search()   # 注意这里 是一个标签
        total = int(re.compile('(\d+)').search(total_element.text).group(1))  # 注意这里 是一个标签，要用text取其中的值
        # print('total:', total)   # 匹配出来的是 str 类型
        for i in range(2, total+1):    # 这里range里面是从第二页开始，第一页请求时自动加载了， i为页码，所以不能为0
            switch_to_page(i)
    except Exception:
        print('出错啦')
    finally:
        browser.close()   # 程序结束时，记得关闭浏览器

if __name__ == '__main__':
    main()