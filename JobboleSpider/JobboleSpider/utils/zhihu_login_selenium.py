import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import sys

# 获取 现在本地已经存在的cookies
profile_dir=r"/home/txowner/.cache/google-chrome"    # 对应你的chrome的用户数据存放路径
chrome_options=webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir="+os.path.abspath(profile_dir))

browser=webdriver.Chrome(chrome_options=chrome_options)
browser.maximize_window()
browser.get("https://www.zhihu.com/")

#
# browser = webdriver.Chrome()
# wait = WebDriverWait(browser, 10)
#
#
# def get_login_page():
#     """
#     一步步跳转到登录页面
#     :return:
#     """
#     try:
#         browser.get('https://www.zhihu.com/')
#
#         # 找到 '登录' 按钮
#         login = wait.until(EC.element_to_be_clickable(
#             (By.CSS_SELECTOR, 'body > div.index-main > div > div.desk-front.sign-flow.sign-flow.clearfix.sign-flow-simple > div.index-tab-navs > div > a:nth-child(2)')
#         ))
#         # 点击 '登录' 按钮
#         login.click()
#
#         # 找到 '使用密码登录' 按钮
#         login_use_passwd = wait.until(EC.element_to_be_clickable(
#             (By.CSS_SELECTOR, 'body > div.index-main > div > div.desk-front.sign-flow.sign-flow.clearfix.sign-flow-simple > div.view.view-signin > div.qrcode-signin-container > div.qrcode-signin-step1 > div.qrcode-signin-cut-button > span')
#         ))
#         # 点击 '使用密码登录' 按钮
#         login_use_passwd.click()
#
#         # 找到 账号、密码 输入框
#         account = wait.until(EC.presence_of_element_located(
#             (By.CSS_SELECTOR, 'body > div.index-main > div > div.desk-front.sign-flow.sign-flow.clearfix.sign-flow-simple > div.view.view-signin > form > div.group-inputs > div.account.input-wrapper > input[type="text"]')
#         ))
#         password = wait.until(EC.presence_of_element_located(
#             (By.CSS_SELECTOR, 'body > div.index-main > div > div.desk-front.sign-flow.sign-flow.clearfix.sign-flow-simple > div.view.view-signin > form > div.group-inputs > div.verification.input-wrapper > input[type="password"]')
#         ))
#
#         # 向 找到的 账号、密码 输入框 中输入数据
#         account.clear()   # 清空输入框，防止以前有数据
#         account.send_keys('13281826916')
#         password.clear()
#         password.send_keys('tianxu7098++')
#
#     except TimeoutException:
#         get_login_page()
#
#
#
#
# def post_login(user, password):
#     """
#     请求知乎登录接口，并发送数据
#     :param user:   账户
#     :param password:   密码
#     :return:
#     """
#     pass
#
#
#
# if __name__ == '__main__':
#     get_login_page()