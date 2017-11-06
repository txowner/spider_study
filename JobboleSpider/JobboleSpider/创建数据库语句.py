
# 创建数据库语句：
"""
    CREATE DATABASE `jobbole_spider` DEFAULT CHARSET 'utf8';

"""

# 创建表语句：
"""
    CREATE TABLE IF NOT EXISTS `jobbole_article` (
       url_object_id VARCHAR(50) NOT NULL,
       url VARCHAR(200) NOT NULL,
       front_image_url VARCHAR(200) NULL,
       title VARCHAR(200) NOT NULL,
       create_data DATE NOT NULL,
       tags VARCHAR(50) NULL,
       thumbs_up INT(10) NULL,
       collected INT(10) NULL,
       comments INT(10) NULL,
       content LONGTEXT,
       PRIMARY KEY ( url_object_id )
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

"""