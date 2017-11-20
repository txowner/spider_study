# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb


class GetIp(object):
    def __init__(self):
        self.url = 'http://www.xicidaili.com/nn/{0}'
        self.headers =  {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
        }
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='jobbole_spider', charset='utf8')
        self.cursor = self.conn.cursor()
        self.main()

    def __get_xici(self, n):
        """
        请求西刺代理，获取 代理ip 端口
        :return: 
        """
        try:
            response = requests.get(url=self.url.format(n), headers=self.headers)
            if response.status_code >= 200 and response.status_code <=206:
                return response.text
            else:
                count = 3
                while count:
                    self.__get_xici(n)
                    count -= 1
                print('Get IP Falied')
                return None
        except Exception as e:
            print(e)

    def __parse_page(self, html):
        """
        解析每一页的html代码，从中获取ip端口等
        :return: 
        """
        if html:
            ip_list = []
            response = Selector(text=html)
            tr_list = response.css('#ip_list tr')
            for node in tr_list[1:]:
                node_info = node.css('td::text').extract()
                ip = node_info[0]
                port = node_info[1]
                type = node_info[5] if node_info[5].strip() else 'HTTP'
                speed = float(node.css('.bar::attr(title)').re('\d+.\d+')[0])
                ip_list.append((ip, port, type, speed))

            return ip_list
        else:
            print('No result')
            return None

    def __save2mysql(self, ip_list):
        """
        把获取道德ip插入mysql数据库
        :return: 
        """
        if ip_list:
            for ip_info in ip_list:
                insert_sql = """
                    INSERT INTO xici_ip(ip, port, type, speed) VALUES ('{0}', '{1}', '{2}', '{3}') 
                    ON DUPLICATE KEY UPDATE port=VALUES(port), type=VALUES(type), speed=VALUES(speed)
                """.format(*ip_info)
                self.cursor.execute(insert_sql)
                self.conn.commit()

    def __del_ip(self, ip):
        """
        从数据库删除一条记录
        :return: 
        """
        del_sql = """
            DELETE FROM xici_ip WHERE ip = '{0}'
        """.format(ip)
        self.cursor.execute(del_sql)
        self.conn.commit()

    def random_ip(self):
        """
        通过请求百度检查ip的可用性
        :return: 
        """
        random_sql = """
            SELECT * FROM xici_ip ORDER BY RAND() LIMIT 1
        """
        self.cursor.execute(random_sql)
        res = self.cursor.fetchall()[0]
        ip, port, type, speed = res
        proxies = {
            type: '{0}:{1}'.format(ip, port),
        }
        response = requests.get(url='https://www.baidu.com', proxies=proxies)
        if response.status_code >= 200 and response.status_code <= 206:
            ip = '{0}:{1}'.format(ip, port)
            self.__del_ip(ip)
            return ip
        else:
            self.__del_ip(ip)
            self.random_ip()

    def main(self):
        """
        完成初始化
        :return: 
        """
        for n in range(1,2500):
            html = self.__get_xici(n)
            ip_list = self.__parse_page(html)
            self.__save2mysql(ip_list)



if __name__ == '__main__':
    G = GetIp()
    ip = G.random_ip()
    print(ip)