# coding: utf-8
import os
import loggus
import pymysql

config = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "database": os.environ.get("MYSQL_DB", "mysql"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PWD", "root"),
    "autocommit": True,
}

loggus.withFields(config).info("连接MySQL数据库...")
try:
    db = pymysql.connect(**config)
except:
    loggus.withFieldTrace().panic("连接MySQL失败")
else:
    loggus.info("连接MySQL成功！")


def excute(sql):
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results
