# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/7
import os,sys
import setproctitle
import psutil
import time, datetime
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config

def green_print(*msg):
    for _ in msg:
        print('\033[92m%s \033[0m' % _,end=' ')
    print('')


def red_print(*msg):
    for _ in msg:
        print('\033[91m%s \033[0m' % _, end=' ')
    print('')


def yellow_print(*msg):
    for _ in msg:
        print('\033[93m%s \033[0m' % _, end=' ')
    print('')

if __name__ == '__main__':
    import mysql.connector
    mysql_conn = mysql.connector.connect(host=config.MYSQL_HOST, port=config.MYSQL_PORT,
                                         db=config.MYSQL_DB, user=config.MYSQL_USER,
                                         passwd=config.MYSQL_PASSWORD, charset='utf8')
    cursor = mysql_conn.cursor()
    cursor.execute("show tables")
    info = cursor.fetchall()
    if len(info) != 0:
        red_print("当前数据库非空，不允许执行数据库初始化！")
    else:
        #sql_content = ''
        green_print("开始执行SQL...")
        with open(os.path.join(BASE_PATH, "db.sql"), "r") as f:
            sql_content = f.read()
        # print(sql_content)
        result_iterator = cursor.execute(sql_content, multi=True)
        for res in result_iterator:
            print("Running query: ", res)  # Will print out a short representation of the query
            print(f"Affected {res.rowcount} rows")
            #mysql_conn.commit()
        mysql_conn.commit()
        cursor.execute("show tables")
        info = cursor.fetchall()
        for table in info:
            table = table[0]
            if table.startswith("django") or table.startswith("auth"):
                pass
            else:
                truncate_sql = f"truncate table {table }"
                green_print(truncate_sql)
                cursor.execute(truncate_sql)
                mysql_conn.commit()
        green_print("初始化完成 系统初始登录密码为 admin  123456")


    cursor.close()
    mysql_conn.close()
    #print(info)
