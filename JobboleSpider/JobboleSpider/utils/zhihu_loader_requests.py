# 模拟 知乎 登录

import requests
from requests.exceptions import RequestException
import re


headers = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
}


def get_xsrf():
    """
    获取登录时发送的参数xref的值
    :return: 
    """
    try:
        response = requests.get('https://www.zhihu.com', headers=headers)
        result = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.S)
        print(result.group(1))
        return result.group(1)

    except RequestException:
        print('请求xref code错误')


def get_login(user, password):
    """
    请求知乎登录接口，并发送数据
    :param user:   账户 
    :param password:   密码
    :return: 
    """
    try:
        base_login_url = 'https://www.zhihu.com/login/'
        if '@' in user:
            print('email账号登录')
            post_data = {
                '_xsrf': '63326530643562352d326332622d346661362d393061332d323038336136613761326237',
                'email': user,
                'password': password,
                'captcha_type': 'cn',
            }
            response = requests.post(base_login_url+'email', data=post_data, headers=headers)
        else:
            print('手机账号登录')
            post_data = {
                '_xsrf': '63326530643562352d326332622d346661362d393061332d323038336136613761326237',
                'phone_num': user,
                'password': password,
                'captcha_type': 'cn',
            }
            response = requests.post(base_login_url + 'phone_num', data=post_data, headers=headers)

        print(response.text)

    except RequestException:
        get_login(user, password)


if __name__ == '__main__':
    get_login('13281826916', 'tianxu7098++')
    # get_xsrf()