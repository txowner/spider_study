import requests
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# response = requests.get('http://127.0.0.1:5000', auth=('txowner', 'tianxuroot'))

browser = webdriver.Chrome()
browser.get('https://www.zhihu.com/#signin')

wait = WebDriverWait('browser', 10)
wait.until()



# headers = {
# 	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
# }
# data = {'account': '13281826916', 'password': 'tianxu7098'}

# response = requests.post('', data=data, headers=headers)

# print(response.text)