from hashlib import md5


def get_md5(value):
    m = md5()
    if isinstance(value, str):
        value = value.encode('utf8')
    m.update(value)
    return m.hexdigest()


if __name__ == '__main__':
    s = 'http://jobbole.com'
    print(type(s))
    a = get_md5(s)
    print(a)