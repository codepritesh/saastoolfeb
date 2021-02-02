import mysql.connector
from mysql_db import *
import time 


#{"own_name":"pmpmaharana97@gmail.com","uuid":"1b9d7c40-3e00-11eb-a441-2b120880487d","ex_id":"BIN","api_name":"rohitsirapi","amount":"0.001","pair":"BTC/USDT","profit":"10","timer":"10","postOnly":false,"port":"8000","signal":"start","is_production":false}

def sql_orderid_status(order_id,status,webinput_botfather):
	table_exist = table_exists()
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor  = mysqlconn.cursor()
	ts = time.time()
	sql = "insert into orderid_status_table(order_id,status,time) values(%s,%s,%s)"
	val = (str(order_id),str(status),str(ts))
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	print("statusdata_form_bot_father.py",webinput_botfather)
	return True