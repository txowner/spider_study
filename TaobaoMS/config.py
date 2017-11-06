
# MongoDB 配置
MONGO_HOST = 'localhost'
MONGO_DB = 'taobao'

# 爬虫爬取设置
KEYWORD = '女款大衣'

# 设置关键字 就在下面添加对应的数据库键值对
KEYWORD_TABLE = {
    '美食': 'delicious',
    '电脑': 'computers',
    '女款大衣': 'girls',
    '背包': 'packages',
    '苹果电脑': 'apple',
}

# PhantomJS 配置
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

# --load-images=[true|false]   是否加载图片，减少网络请求
# --disk-cache=[true|false]    是否启用缓存

# 详情见：   http://phantomjs.org/api/command-line.html



if __name__ == '__main__':
    print(KEYWORD_TABLE[KEYWORD])