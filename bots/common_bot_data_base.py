
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from mysql_db import *
import time 
from pprint import pprint


def get_database_data(username):
	fetch_all_bot=sql_get_all_fetch(username)
	#print('allllllllll--------------------------',fetch_all_bot)

	bot_one=cancel_avg_tool_fetch(username)
	#print('one--------------------------',bot_one)

	bot_two=support_big_amount_bot_fetch(username)
	#print('two------------------------------',bot_two)

	bot_three=support_trailing_stop_bot_fetch(username)
	#print('three-------------------------------',bot_three)

	bot_four=arb_2way_tool_fetch(username)
	#print('four------------------------------',bot_four)

	bot_five=atr_trailing_stop_bot_tool_fetch(username)
	#print('five-----------------------------',bot_five)

	bot_six=two_way_sp_tool_fetch(username)
	#print('six------------------------------',bot_six)

	bot_seven=support_multi_box_fetch(username)
	#print('seven-----------------------------',bot_seven)

	bot_eight=bs_sb_continuously_tool_fetch(username)
	#print('eight-----------------------------',bot_eight)
	result_bot= {**fetch_all_bot,**bot_one,**bot_two,**bot_three,**bot_four,**bot_five,**bot_six,**bot_seven,**bot_eight,} # | bot_three|bot_four|bot_five|bot_six|bot_seven|bot_eight
	#print("-----------------result_bot-------------------------")
	#pprint(result_bot)

	return result_bot




def sql_get_all_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select order_details_price_table.id,\
             order_details_price_table.database_bot_name,\
             order_details_price_table.timestamp,\
             order_details_price_table.order_id,\
             order_details_price_table.pair,\
             order_details_price_table.order_type,\
             order_details_price_table.side,\
             order_details_price_table.amount,\
             order_details_price_table.price,\
             order_details_price_table.status,\
             order_details_price_table.ex_id,\
             order_details_price_table.api_name\
             from order_details_price_table\
             where order_details_price_table.own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			formated_order_id=str(resultdict[str(i)]["order_id"])
			formated_status=str(resultdict[str(i)]["status"])
			#print("------------------------------status--------status",formated_status)
			#print("------------------------------formated_order_id--------formated_order_id",formated_order_id)

			#if formated_status == '':
				#order_id_status=status_from_cancled_order_table(formated_order_id)


			i=i+1
		mycursor.close()
		dummy={'1': {'amount': ' ',
		'api_name': ' ',
		'database_bot_name': ' ',
		'ex_id': ' ',
		'id': ' ',
		'order_id': ' ',
		'order_type': ' ',
		'pair': ' ',
		'price': ' ',
		'side': ' ',
		'status': ' ',
		'timestamp': ' '},
		'2': {'amount': ' ',
		'api_name': ' ',
		'database_bot_name': ' ',
		'ex_id': ' ',
		'id': ' ',
		'order_id': ' ',
		'order_type': ' ',
		'pair': ' ',
		'price': ' ',
		'side': ' ',
		'status': ' ',
		'timestamp': ' '},
		'3': {'amount': ' ',
		'api_name': ' ',
		'database_bot_name': ' ',
		'ex_id': ' ',
		'id': ' ',
		'order_id': ' ',
		'order_type': ' ',
		'pair': ' ',
		'price': ' ',
		'side': ' ',
		'status': ' ',
		'timestamp': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		all_bot_dict={"all_bot":resultdict}
		#print('0sql_get_all_fetch')
		#pprint(myresult)
		#pprint(resultdict)
		
		return all_bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data---sql_get_all_fetch {}".format(error))
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()




def cancel_avg_tool_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from clear_order_bot_table where own_name='{}' order by id desc limit 3".format(str(username))

		'''
		sql="select cancled_order_table.id,\
             cancled_order_table.database_bot_name,\
             cancled_order_table.timestamp,\
             cancled_order_table.order_id,\
             cancled_order_table.order_status,\
             order_details_price_table.pair,\
             order_details_price_table.order_type,\
             order_details_price_table.side,\
             order_details_price_table.amount,\
             order_details_price_table.price\
             from cancled_order_table\
             left join order_details_price_table\
             on cancled_order_table.order_id=order_details_price_table.order_id\
             where cancled_order_table.own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		#print(sql)
		'''
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'accu_amount': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'avg_price': ' ',
		       'creation_time': ' ',
		       'ex_id': ' ',
		       'id': '',
		       'input_pair': ' ',
		       'input_side': ' ',
		       'input_signal': ' ',
		       'is_using': ' ',
		       'order_id': ' ',
		       'order_status': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'price': ' ',
		       'price_type': ' ',
		       'side': ' ',
		       'timestamp': ' ',
		       'update_time': ' ',
		       'uuid': ' '},
		 '2': {'accu_amount': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'avg_price': ' ',
		       'creation_time': ' ',
		       'ex_id': ' ',
		       'id': ' ',
		       'input_pair': ' ',
		       'input_side': ' ',
		       'input_signal': ' ',
		       'is_using': ' ',
		       'order_id': ' ',
		       'order_status': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'price': ' ',
		       'price_type': ' ',
		       'side': ' ',
		       'timestamp': ' ',
		       'update_time': ' ',
		       'uuid': ' '},
		 '3': {'accu_amount': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'avg_price': ' ',
		       'creation_time': ' ',
		       'ex_id': ' ',
		       'id': ' ',
		       'input_pair': ' ',
		       'input_side': ' ',
		       'input_signal': ' ',
		       'is_using': ' ',
		       'order_id': ' ',
		       'order_status': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'price': ' ',
		       'price_type': ' ',
		       'side': ' ',
		       'timestamp': ' ',
		       'update_time': ' ',
		       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot1":resultdict}
		#print('1cancel_avg_tool_fetch')
		#pprint(myresult)
		#pprint(resultdict)		
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data cancel_avg_tool_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()

def support_big_amount_bot_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from support_big_amount_strategy_bot_table where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'amount': ' ',
				'api_name': ' ',
				'average': ' ',
				'ex_id': ' ',
				'filled': ' ',
				'follow_gap': ' ',
				'gap': ' ',
				'id': ' ',
				'order_id': ' ',
				'own_name': ' ',
				'pair': ' ',
				'place_order_profit': ' ',
				'place_order_stop_loss': ' ',
				'position': ' ',
				'postOnly': ' ',
				'price': ' ',
				'profit': ' ',
				'status': ' ',
				'stop_loss': ' ',
				'symbol': ' ',
				'timestamp': ' ',
				'trailing_margin': ' ',
				'uuid': ' '},
				'2': {'amount': ' ',
				'api_name': ' ',
				'average': ' ',
				'ex_id': ' ',
				'filled': ' ',
				'follow_gap': ' ',
				'gap': ' ',
				'id': ' ',
				'order_id': ' ',
				'own_name': ' ',
				'pair': ' ',
				'place_order_profit': ' ',
				'place_order_stop_loss': ' ',
				'position': ' ',
				'postOnly': ' ',
				'price': ' ',
				'profit': ' ',
				'status': ' ',
				'stop_loss': ' ',
				'symbol': ' ',
				'timestamp': ' ',
				'trailing_margin': ' ',
				'uuid': ' '},
				'3': {'amount': ' ',
				'api_name': ' ',
				'average': ' ',
				'ex_id': ' ',
				'filled': ' ',
				'follow_gap': ' ',
				'gap': ' ',
				'id': ' ',
				'order_id': ' ',
				'own_name': ' ',
				'pair': ' ',
				'place_order_profit': ' ',
				'place_order_stop_loss': ' ',
				'position': ' ',
				'postOnly': ' ',
				'price': ' ',
				'profit': ' ',
				'status': ' ',
				'stop_loss': ' ',
				'symbol': ' ',
				'timestamp': ' ',
				'trailing_margin': ' ',
				'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot2":resultdict}
		#print('2support_big_amount_bot_fetch')
		#pprint(myresult)
		#pprint(resultdict)				
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data sql_get_cancel_avg_tool {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()
def support_trailing_stop_bot_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from support_trailing_stop_bot_table where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["trailing_margin"])
			resultdict[str(i)]["trailing_margin"]=formated_timestamp

			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'amount': ' ',
			       'api_name': ' ',
			       'average': ' ',
			       'cancel_threshold': ' ',
			       'entry_price': ' ',
			       'ex_id': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'gap': ' ',
			       'id': ' ',
			       'input_amount': ' ',
			       'input_pair': ' ',
			       'input_trl_margin': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '},
			 '2': {'amount': ' ',
			       'api_name': ' ',
			       'average': ' ',
			       'cancel_threshold': ' ',
			       'entry_price': ' ',
			       'ex_id': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'gap': ' ',
			       'id': ' ',
			       'input_amount': ' ',
			       'input_pair': ' ',
			       'input_trl_margin': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '},
			 '3': {'amount': ' ',
			       'api_name': ' ',
			       'average': ' ',
			       'cancel_threshold': ' ',
			       'entry_price': ' ',
			       'ex_id': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'gap': ' ',
			       'id': ' ',
			       'input_amount': ' ',
			       'input_pair': ' ',
			       'input_trl_margin': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot3":resultdict}
		#print('3support_trailing_stop_bot_fetch')
		#pprint(myresult)
		#pprint(resultdict)					
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data support_trailing_stop_bot_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()
def arb_2way_tool_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from arb_2way_tool_table where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'amount': ' ',
			       'api_name1': ' ',
			       'api_name2': ' ',
			       'average': ' ',
			       'ex_id1': ' ',
			       'ex_id2': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'follow_market': ' ',
			       'gap': ' ',
			       'id':  ' ',
			       'input_price': ' ',
			       'is_parallel': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'profit': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '},
			 '2': {'amount': ' ',
			       'api_name1': ' ',
			       'api_name2': ' ',
			       'average': ' ',
			       'ex_id1': ' ',
			       'ex_id2': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'follow_market': ' ',
			       'gap': ' ',
			       'id':  ' ',
			       'input_price': ' ',
			       'is_parallel': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'profit': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '},
			 '3': {'amount': ' ',
			       'api_name1': ' ',
			       'api_name2': ' ',
			       'average': ' ',
			       'ex_id1': ' ',
			       'ex_id2': ' ',
			       'filled': ' ',
			       'follow_gap': ' ',
			       'follow_market': ' ',
			       'gap': ' ',
			       'id':  ' ',
			       'input_price': ' ',
			       'is_parallel': ' ',
			       'min_profit': ' ',
			       'order_id': ' ',
			       'own_name': ' ',
			       'position': ' ',
			       'postOnly': ' ',
			       'price': ' ',
			       'profit': ' ',
			       'status': ' ',
			       'symbol': ' ',
			       'timestamp': ' ',
			       'trailing_margin': ' ',
			       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot4":resultdict}
		#print('4arb_2way_tool_fetch')
		#pprint(myresult)
		#pprint(resultdict)					
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data arb_2way_tool_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()

def atr_trailing_stop_bot_tool_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from atr_trailing_bot_table where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["timestamp"])
			resultdict[str(i)]["timestamp"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'api_name': ' ',
		       'average': ' ',
		       'bot_amount': ' ',
		       'bot_price': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'input_base_amount': ' ',
		       'input_fees': ' ',
		       'input_price': ' ',
		       'input_profit': ' ',
		       'input_trailing_margin': ' ',
		       'order_id': ' ',
		       'order_trl_margin': ' ',
		       'own_name': ' ',
		       'position': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timestamp': ' ',
		       'trade_id': ' ',
		       'uuid': ' '},
		 '2': {'api_name': ' ',
		       'average': ' ',
		       'bot_amount': ' ',
		       'bot_price': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'input_base_amount': ' ',
		       'input_fees': ' ',
		       'input_price': ' ',
		       'input_profit': ' ',
		       'input_trailing_margin': ' ',
		       'order_id': ' ',
		       'order_trl_margin': ' ',
		       'own_name': ' ',
		       'position': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timestamp': ' ',
		       'trade_id': ' ',
		       'uuid': ' '},
		 '3': {'api_name': ' ',
		       'average': ' ',
		       'bot_amount': ' ',
		       'bot_price': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'input_base_amount': ' ',
		       'input_fees': ' ',
		       'input_price': ' ',
		       'input_profit': ' ',
		       'input_trailing_margin': ' ',
		       'order_id': ' ',
		       'order_trl_margin': ' ',
		       'own_name': ' ',
		       'position': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timestamp': ' ',
		       'trade_id': ' ',
		       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot5":resultdict}
		#print('5atr_trailing_stop_bot_tool_fetch')
		#pprint(myresult)
		#pprint(resultdict)			
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data atr_trailing_stop_bot_tool_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()
def two_way_sp_tool_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from two_way_sp_strategy_bot where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["order_time"])
			resultdict[str(i)]["order_time"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_gap': ' ',
		       'follow_market': ' ',
		       'gap': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'min_profit': ' ',
		       'order_amount': ' ',
		       'order_id': ' ',
		       'order_time': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair2': ' ',
		       'pair_first': ' ',
		       'pair_symbol': ' ',
		       'position': ' ',
		       'postOnly': ' ',
		       'price': ' ',
		       'side': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'trailing_margin': ' ',
		       'uuid': ' '},
		 '2': {'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_gap': ' ',
		       'follow_market': ' ',
		       'gap': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'min_profit': ' ',
		       'order_amount': ' ',
		       'order_id': ' ',
		       'order_time': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair2': ' ',
		       'pair_first': ' ',
		       'pair_symbol': ' ',
		       'position': ' ',
		       'postOnly': ' ',
		       'price': ' ',
		       'side': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'trailing_margin': ' ',
		       'uuid': ' '},
		 '3': {'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_gap': ' ',
		       'follow_market': ' ',
		       'gap': ' ',
		       'id': ' ',
		       'input_amount': ' ',
		       'min_profit': ' ',
		       'order_amount': ' ',
		       'order_id': ' ',
		       'order_time': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair2': ' ',
		       'pair_first': ' ',
		       'pair_symbol': ' ',
		       'position': ' ',
		       'postOnly': ' ',
		       'price': ' ',
		       'side': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'trailing_margin': ' ',
		       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot6":resultdict}
		#print('6two_way_sp_tool_fetch')
		#pprint(myresult)
		#pprint(resultdict)				
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data two_way_sp_tool_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()
def support_multi_box_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from support_multi_box_strategy_bot where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["ts_time"])
			resultdict[str(i)]["ts_time"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'balance_box_amount': ' ',
		       'balance_box_count': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_balance_box_amount': ' ',
		       'follow_balance_box_count': ' ',
		       'follow_balance_box_follow_gap': ' ',
		       'follow_balance_box_gap': ' ',
		       'follow_balance_box_postOnly': ' ',
		       'follow_balance_box_profit': ' ',
		       'follow_balance_box_step': ' ',
		       'follow_balance_box_time': ' ',
		       'follow_track_box_amount': ' ',
		       'follow_track_box_follow_gap': ' ',
		       'follow_track_box_gap': ' ',
		       'follow_track_box_postOnly': ' ',
		       'id': ' ',
		       'inti_box_buy_price': ' ',
		       'inti_box_sell_price': ' ',
		       'order_id': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'position': ' ',
		       'price': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'ts_time': ' ',
		       'uuid': ' '},
		 '2': {'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'balance_box_amount': ' ',
		       'balance_box_count': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_balance_box_amount': ' ',
		       'follow_balance_box_count': ' ',
		       'follow_balance_box_follow_gap': ' ',
		       'follow_balance_box_gap': ' ',
		       'follow_balance_box_postOnly': ' ',
		       'follow_balance_box_profit': ' ',
		       'follow_balance_box_step': ' ',
		       'follow_balance_box_time': ' ',
		       'follow_track_box_amount': ' ',
		       'follow_track_box_follow_gap': ' ',
		       'follow_track_box_gap': ' ',
		       'follow_track_box_postOnly': ' ',
		       'id': ' ',
		       'inti_box_buy_price': ' ',
		       'inti_box_sell_price': ' ',
		       'order_id': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'position': ' ',
		       'price': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'ts_time': ' ',
		       'uuid': ' '},
		 '3': {'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'balance_box_amount': ' ',
		       'balance_box_count': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'follow_balance_box_amount': ' ',
		       'follow_balance_box_count': ' ',
		       'follow_balance_box_follow_gap': ' ',
		       'follow_balance_box_gap': ' ',
		       'follow_balance_box_postOnly': ' ',
		       'follow_balance_box_profit': ' ',
		       'follow_balance_box_step': ' ',
		       'follow_balance_box_time': ' ',
		       'follow_track_box_amount': ' ',
		       'follow_track_box_follow_gap': ' ',
		       'follow_track_box_gap': ' ',
		       'follow_track_box_postOnly': ' ',
		       'id': ' ',
		       'inti_box_buy_price': ' ',
		       'inti_box_sell_price': ' ',
		       'order_id': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'position': ' ',
		       'price': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'ts_time': ' ',
		       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot7":resultdict}
		#print('7support_multi_box_fetch')
		#pprint(myresult)
		#pprint(resultdict)				
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data support_multi_box_strategy_bot {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()
def bs_sb_continuously_tool_fetch(username):
	try:
		mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=mysqlconn.cursor(dictionary=True)
		sql="select * from tool_buysell_sellbuy_continuously where own_name='{}' order by id desc limit 3".format(str(username))
		#print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchall()
		resultdict={}
		i=1
		for dic1 in myresult:
			resultdict[str(i)]= dic1
			formated_timestamp=str(resultdict[str(i)]["update_date_time"])
			resultdict[str(i)]["update_date_time"]=formated_timestamp
			i=i+1
		mycursor.close()
		dummy={'1': {'action': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'order_id': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'port': ' ',
		       'position': ' ',
		       'postOnly':' ',
		       'price': ' ',
		       'profit': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timer': ' ',
		       'trade_id': ' ',
		       'trailing_margin': ' ',
		       'update_date_time': ' ',
		       'uuid': ' '},
		 '2': {'action': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'order_id': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'port': ' ',
		       'position': ' ',
		       'postOnly':' ',
		       'price': ' ',
		       'profit': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timer': ' ',
		       'trade_id': ' ',
		       'trailing_margin': ' ',
		       'update_date_time': ' ',
		       'uuid': ' '},
		 '3': {'action': ' ',
		       'amount': ' ',
		       'api_name': ' ',
		       'average': ' ',
		       'ex_id': ' ',
		       'filled': ' ',
		       'id': ' ',
		       'order_id': ' ',
		       'ori_amount': ' ',
		       'ori_price': ' ',
		       'own_name': ' ',
		       'pair': ' ',
		       'port': ' ',
		       'position': ' ',
		       'postOnly':' ',
		       'price': ' ',
		       'profit': ' ',
		       'status': ' ',
		       'symbol': ' ',
		       'timer': ' ',
		       'trade_id': ' ',
		       'trailing_margin': ' ',
		       'update_date_time': ' ',
		       'uuid': ' '}}
		dummy.update(resultdict)
		resultdict = dummy
		bot_dict={"bot8":resultdict}
		#print('8bs_sb_continuously_tool_fetch')
		#pprint(myresult)
		#pprint(resultdict)		
		return bot_dict

	except mysql.connector.Error as error:
		print("Failed to fetch data bs_sb_continuously_tool_fetch {}".format(error))
		
	finally:
		if (mysqlconn.is_connected()):
			mysqlconn.close()





