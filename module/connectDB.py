import pymysql # mysql
import json

# 連接資料庫
def setting():
    file = open("db_settings.json")
    config = json.load(file)
    try:
        # 建立Connection物件
        connection = pymysql.connect(**config)
        # connection = mysql.connector.connect(**config)
        print("==========success to connect DB=============")
        return connection
    except Exception as ex:
        print("error",ex)
        return
# 建立連結
connection = setting()
cursor = connection.cursor()
