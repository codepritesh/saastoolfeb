import mysql.connector
from mysql_db import *
import time
from datetime import datetime


def get_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor(dictionary=True)
	#now_time = datetime.fromtimestamp(time.time())
	#str_time = str(now_time)
	#ts = str_time[:-7]
	sql = "select * from order_details_price_table where (own_name ='{}' and database_bot_name='{}') and (timestamp >= '{}' and timestamp <= '{}')order by id desc".format(input_user_name,input_bot_name,input_trade_start,input_trade_end)
	
	
	mycursor.execute(sql)
	data_result = mycursor.fetchall()
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("------------------------------",data_result)
	
	return data_result

def get_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor(dictionary=True)
	#now_time = datetime.fromtimestamp(time.time())
	#str_time = str(now_time)
	#ts = str_time[:-7]
	sql = "select * from order_details_price_table where (own_name ='{}') and (timestamp >= '{}' and timestamp <= '{}')order by id desc".format(input_user_name,input_trade_start,input_trade_end)
	
	
	mycursor.execute(sql)
	data_result = mycursor.fetchall()
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("------------------------------",data_result)
	
	return data_result
def get_all_user_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor(dictionary=True)
	#now_time = datetime.fromtimestamp(time.time())
	#str_time = str(now_time)
	#ts = str_time[:-7]
	sql = "select * from order_details_price_table where (timestamp >= '{}' and timestamp <= '{}')order by id desc".format(input_trade_start,input_trade_end)
	
	
	mycursor.execute(sql)
	data_result = mycursor.fetchall()
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("------------------------------",data_result)
	
	return data_result

def get_all_user_single_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor(dictionary=True)
	#now_time = datetime.fromtimestamp(time.time())
	#str_time = str(now_time)
	#ts = str_time[:-7]
	sql = "select * from order_details_price_table where database_bot_name='{}' and (timestamp >= '{}' and timestamp <= '{}')order by id desc".format(input_bot_name,input_trade_start,input_trade_end)
	
	
	mycursor.execute(sql)
	data_result = mycursor.fetchall()
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("------------------------------",data_result)
	
	return data_result

