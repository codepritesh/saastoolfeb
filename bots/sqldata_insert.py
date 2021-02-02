import mysql.connector
from mysql_db import *
import time
from datetime import datetime
'''
 #if type(webinput_botfather["pair"]) is list:
        #pair_list = webinput_botfather["pair"]   
        #pair_string = ','.join([str(elem) for elem in pair_list])

        #if "inti_box_amount" in webinput_botfather.keys():
         #   webinput_botfather["amount"] = webinput_botfather.pop("inti_box_amount")
        #else:
        #print("LINE----------105")


         else:
    	if "ex_id1" in webinput_botfather.keys():
    		webinput_botfather["ex_id"] = webinput_botfather.pop("ex_id1")
    	if "inti_box_amount" in webinput_botfather.keys():
    		webinput_botfather["amount"] = webinput_botfather.pop("inti_box_amount")
    	if "api_name1" in webinput_botfather.keys():
    		webinput_botfather["api_name"] = webinput_botfather.pop("api_name1")
    	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
    	mycursor  = mysqlconn.cursor()
    	now_time = datetime.fromtimestamp(time.time())
    	str_time = str(now_time)
    	ts = str_time[:-7]
    	sql = "insert into orderid_status_table(order_id,status,time,own_name,uuid,ex_id,api_name,pair,amount) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    	val = (str(order_id),
    		str(status),
			str(ts),
			str(webinput_botfather['own_name']),
			str(webinput_botfather['uuid']),
			str(webinput_botfather['ex_id']),
			str(webinput_botfather['api_name']),
			str(webinput_botfather['pair']),
			str(webinput_botfather['amount']),
			)
    	mycursor.execute(sql,val)
    	mysqlconn.commit()
    	mycursor.close()
    	mysqlconn.close()
    	print("-sqldata_insert-------------------149",webinput_botfather)
    	print("LINE-----sqldata_insert--------150")

'''


#dataexample={'order_id': '3884051111', 'status': 'closed', 'symbol': 'BTC/USDT', 'filled': 0.001, 'average': 18334.21, 'position': 'buy', 'amount': 0.001, 'params': {}, 'price': 18335.14, 'meta_data': {'own_name': 'pmpmaharana97@gmail.com', 'uuid': 'd1203ce0-3c3b-11eb-b2f0-cd03c264bdd2', 'ex_id': 'BIN', 'api_name': 'rohitsirapi', 'amount': '0.001', 'pair': 'BTC/USDT', 'profit': '0.2', 'timer': '10', 'postOnly': True, 'port': '8000', 'action': 'buy/sell', 'framework': 'Django', 'trade_id': '1', 'ori_price': 18335.14, 'ori_amount': 0.001}, 'trailing_margin': None}


def sql_insertbssb(data):

	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(data['order_id'])
	str_order_status = str(data['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into tool_buysell_sellbuy_continuously(order_id,status,symbol,filled,average,position,amount,price,own_name,uuid,ex_id,api_name,pair,profit,timer,postOnly,port,action,trade_id,ori_price,ori_amount,trailing_margin,update_date_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(data['order_id']),
		str(data['status']),
		str(data['symbol']),
		str(data['filled']),
		str(data['average']),
		str(data['position']),
		str(data['amount']),
		str(data['price']),
		str(data['meta_data']['own_name']),
		str(data['meta_data']['uuid']),
		str(data['meta_data']['ex_id']),
		str(data['meta_data']['api_name']),
		str(data['meta_data']['pair']),
		str(data['meta_data']['profit']),
		str(data['meta_data']['timer']),
		str(int(data['meta_data']['postOnly'])),
		str(data['meta_data']['port']),
		str(data['meta_data']['action']),
		str(data['meta_data']['trade_id']),
		str(data['meta_data']['ori_price']),
		str(data['meta_data']['ori_amount']),
		str(data['trailing_margin']),
		str(ts),
		


		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("sqldata_insert--------------------------48",data)
	return True


def sql_insert_bssb_order_info(data):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	#below 3 lines are responsible for status update
	str_orderid = str(data['order_id'])
	str_order_status = str(data['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into tool_buysell_sellbuy_continuously(order_id,status,symbol,filled,average,position,amount,price,own_name,uuid,ex_id,api_name,pair,profit,timer,postOnly,port,action,trade_id,ori_price,ori_amount,update_date_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(data['order_id']),
		str(data['status']),
		str(data['symbol']),
		str(data['filled']),
		str(data['average']),
		str(data['position']),
		str(data['amount']),
		str(data['price']),
		str(data['meta_data']['own_name']),
		str(data['meta_data']['uuid']),
		str(data['meta_data']['ex_id']),
		str(data['meta_data']['api_name']),
		str(data['meta_data']['pair']),
		str(data['meta_data']['profit']),
		str(data['meta_data']['timer']),
		str(int(data['meta_data']['postOnly'])),
		str(data['meta_data']['port']),
		str(data['meta_data']['action']),
		str(data['meta_data']['trade_id']),
		str(data['meta_data']['ori_price']),
		str(data['meta_data']['ori_amount']),
		str(ts),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("sqldata_insert--------------------------83",data)
	return True


#{"own_name":"pmpmaharana97@gmail.com","uuid":"1b9d7c40-3e00-11eb-a441-2b120880487d","ex_id":"BIN","api_name":"rohitsirapi","amount":"0.001","pair":"BTC/USDT","profit":"10","timer":"10","postOnly":false,"port":"8000","signal":"start","is_production":false}

def sql_orderid_status(order_id,status,database_bot_name,pair,amount,own_name='NA',uuid='NA',ex_id='NA',api_name='NA'):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor  = mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_id)
	str_order_status = str(status)
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql = "insert into orderid_status_table(order_id,status,time,own_name,database_bot_name,uuid,ex_id,api_name,pair,amount) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (str(order_id),
		str(status),
		str(ts),
		str(own_name),
		str(database_bot_name),
		str(uuid),
		str(ex_id),
		str(api_name),
		str(pair),
		str(amount),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("-sqldata_insert----------------------122",webinput_botfather)
	#print("LINE-----sqldata_insert--------123")
def sql_support_multi_box(order_info,own_name='NA',uuid='NA',ex_id='NA',api_name='NA',pair='NA',inti_box_buy_price='NA',inti_box_sell_price='NA',follow_track_box_postOnly='NA',follow_track_box_gap='NA',follow_track_box_follow_gap='NA',follow_track_box_amount='NA',balance_box_amount='NA',balance_box_count='NA',follow_balance_box_postOnly='NA',follow_balance_box_gap='NA',follow_balance_box_follow_gap='NA',follow_balance_box_time='NA',follow_balance_box_amount='NA',follow_balance_box_count='NA',follow_balance_box_profit='NA',follow_balance_box_step='NA'):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)	
	sql= "insert into support_multi_box_strategy_bot(order_id,status,symbol,filled,average,position,amount,price,own_name,uuid,ex_id,api_name,pair,inti_box_buy_price,inti_box_sell_price,follow_track_box_postOnly,follow_track_box_gap,follow_track_box_follow_gap,follow_track_box_amount,balance_box_amount,balance_box_count,follow_balance_box_postOnly,follow_balance_box_gap,follow_balance_box_follow_gap,follow_balance_box_time,follow_balance_box_amount,follow_balance_box_count,follow_balance_box_profit,follow_balance_box_step,ts_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(order_info['order_id']),
		str(order_info['status']),
		str(order_info['symbol']),
		str(order_info['filled']),
		str(order_info['average']),
		str(order_info['position']),
		str(order_info['amount']),
		str(order_info['price']),
		str(own_name),
		str(uuid),
		str(ex_id),
		str(api_name),
		str(pair),
		str(inti_box_buy_price),
		str(inti_box_sell_price),
		str(follow_track_box_postOnly),
		str(follow_track_box_gap),
		str(follow_track_box_follow_gap),
		str(follow_track_box_amount),
		str(balance_box_amount),
		str(balance_box_count),
		str(follow_balance_box_postOnly),
		str(follow_balance_box_gap),
		str(follow_balance_box_follow_gap),
		str(follow_balance_box_time),
		str(follow_balance_box_amount),
		str(follow_balance_box_count),
		str(follow_balance_box_profit),
		str(follow_balance_box_step),
		str(ts),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("-sqldata_insert------------------------196",multi_box_web_input)
	#print("LINE----------199")

def sql_two_way_sp_strategy_bot(order_info,own_name,uuid,ex_id,api_name,amount,pair_string,follow_market,pair_first,min_profit,postOnly,gap,follow_gap,side):
	#pair_list = two_way_web_input["pair"]
	#pair_string = ','.join([str(elem) for elem in pair_list])
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)	
	sql= "insert into two_way_sp_strategy_bot(order_id,status,symbol,filled,average,position,order_amount,price,pair2,ori_price,ori_amount,trailing_margin,own_name,uuid,ex_id,api_name,input_amount,pair_symbol,follow_market,pair_first,min_profit,postOnly,gap,follow_gap,side,order_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(order_info['order_id']),
		str(order_info['status']),
		str(order_info['symbol']),
		str(order_info['filled']),
		str(order_info['average']),
		str(order_info['position']),
		str(order_info['amount']),
		str(order_info['price']),
		str(order_info['meta_data']['pair2']),
		str(order_info['meta_data']['ori_price']),
		str(order_info['meta_data']['ori_amount']),
		str(order_info['trailing_margin']),	    
		str(own_name),
		str(uuid),
		str(ex_id),
		str(api_name),
		str(amount),
		str(pair_string),
		str(follow_market),
		str(pair_first),
		str(min_profit),
		str(postOnly),
		str(gap),
		str(follow_gap),
		str(side),
		str(ts),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("sqldata_insert------------------------255",two_way_web_input)
	#print("LINE-----sqldata_insert--------256")

#pair,type,side,amount,price,order_id,web_input_exchangelib
def sql_exchange_lib_order_details(pair,order_type,side,amount,price,order_id,own_name,bot_name,bot_uuid,api_name,exchange_id):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	sql= "insert into order_details_price_table(api_name,ex_id,own_name,database_bot_name,uuid,timestamp,order_id,pair,order_type,side,amount,price) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(api_name),
		str(exchange_id),
		str(own_name),
		str(bot_name),
		str(bot_uuid),
		str(ts),
		str(order_id),
		str(pair),
		str(order_type),
		str(side),
		str(amount),
		str(price),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("sqldata_insert------------sql_exchange_lib_order_details--------------258",pair,order_type,side,amount,price,order_id)
	return True



def exchange_lib_cancled_order(order_id,order_status,own_name,bot_name,bot_uuid):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_id)
	str_order_status = str(order_status)
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)	
	sql= "insert into cancled_order_table(own_name,database_bot_name,uuid,timestamp,order_id,order_status) values(%s,%s,%s,%s,%s,%s)"
	val = (
		str(own_name),
		str(bot_name),
		str(bot_uuid),
		str(ts),
		str(order_id),
		str(order_status),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	#print("sqldata_insert------------exchange_lib_cancled_order--------------258")
	return True

def sql_insert_atr_trailing_bot(order_info,trade_id,own_name,uuid,ex_id,api_name,amount,price,profit,base_amount,trailing_margin,fees):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into atr_trailing_bot_table(order_id,status,symbol,filled,average,position,bot_amount,bot_price,trade_id,order_trl_margin,own_name,uuid,ex_id,api_name,input_amount,input_price,input_profit,input_base_amount,input_trailing_margin,input_fees,timestamp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
	    str(order_info['order_id']),
	    str(order_info['status']),
	    str(order_info['symbol']),
	    str(order_info['filled']),
	    str(order_info['average']),
	    str(order_info['position']),
	    str(order_info['amount']),
	    str(order_info['price']),
	    str(trade_id),
	    str(order_info['trailing_margin']),
	    str(own_name),
	    str(uuid),
	    str(ex_id),
	    str(api_name),
	    str(amount),	    
	    str(price),
	    str(profit),
	    str(base_amount),
	    str(trailing_margin),
	    str(fees),
	    str(ts),
		)
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	return True
	#print("sqldata_insert----sql_insert_atr_trailing_bot--------------------------83",order_info)
	#print("LINE---sqldata_insert----------311")


def sql_insert_arb_2way_toolbot(order_info,own_name,uuid,ex_id1,api_name1,ex_id2,api_name2,profit,min_profit,price,follow_market,is_parallel,postOnly,gap,follow_gap):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into arb_2way_tool_table(order_id,status,symbol,filled,average,position,amount,price,trailing_margin,own_name,uuid,ex_id1,api_name1,ex_id2,api_name2,profit,min_profit,input_price,follow_market,is_parallel,postOnly,gap,follow_gap,timestamp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(order_info['order_id']),
		str(order_info['status']),
	    str(order_info['symbol']),
	    str(order_info['filled']),
	    str(order_info['average']),
	    str(order_info['position']),
	    str(order_info['amount']),
	    str(order_info['price']),
	    str(order_info['trailing_margin']),
	    str(own_name),
	    str(uuid),
	    str(ex_id1),
	    str(api_name1),
	    str(ex_id2),
	    str(api_name2),
	    str(profit),
	    str(min_profit),
	    str(price),
	    str(follow_market),
	    str(is_parallel),
	    str(postOnly),
	    str(gap),
	    str(follow_gap),
	    str(ts),
	    )
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	return True
	#print("sqldata_insert----sql_insert_arb_2way_tool_table--------------------------83",order_info)
	#print("LINE---sqldata_insert----------311")



def sql_support_trailing_stop_bot(order_info,trade_id,own_name,uuid,ex_id,api_name,amount,pair,entry_price,trailing_margin,cancel_threshold,postOnly,gap,follow_gap,min_profit):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into support_trailing_stop_bot_table(order_id,status,symbol,filled,average,position,amount,price,trailing_margin,own_name,uuid,ex_id,api_name,input_amount,input_pair,entry_price,input_trl_margin,cancel_threshold,postOnly,gap,follow_gap,min_profit,timestamp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(order_info['order_id']),
		str(order_info['status']),
	    str(order_info['symbol']),
	    str(order_info['filled']),
	    str(order_info['average']),
	    str(order_info['position']),
	    str(order_info['amount']),
	    str(order_info['price']),
	    str(order_info['trailing_margin']),
	    str(own_name),
	    str(uuid),
	    str(ex_id),
	    str(api_name),
	    str(amount),
	    str(pair),
	    str(entry_price),
	    str(trailing_margin),
	    str(cancel_threshold),
	    str(postOnly),
	    str(gap),
	    str(follow_gap),	    
	    str(min_profit),
	    str(ts),
	    )
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	return True
	#print("sqldata_insert----sql_support_trailing_stop_bot--------------------------83",arb_web_input)
	#print("LINE---sqldata_insert----------397")





def sql_support_big_amount_strategy_bot(order_info,own_name,uuid,ex_id,api_name,pair,stop_loss,profit,postOnly,gap,follow_gap,place_order_stop_loss,place_order_profit):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	str_orderid = str(order_info['order_id'])
	str_order_status = str(order_info['status'])
	status_for_orderid_update = update_staus_for_orderid(str_orderid,str_order_status)
	sql= "insert into support_big_amount_strategy_bot_table(order_id,status,symbol,filled,average,position,amount,price,trailing_margin,own_name,uuid,ex_id,api_name,pair,stop_loss,profit,postOnly,gap,follow_gap,place_order_stop_loss,place_order_profit,timestamp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(order_info['order_id']),
		str(order_info['status']),
	    str(order_info['symbol']),
	    str(order_info['filled']),
	    str(order_info['average']),
	    str(order_info['position']),
	    str(order_info['amount']),
	    str(order_info['price']),
	    str(order_info['trailing_margin']),
	    str(own_name),
	    str(uuid),
	    str(ex_id),
	    str(api_name),
	    str(pair),
	    str(stop_loss),
	    str(profit),
	    str(postOnly),
	    str(gap),
	    str(follow_gap),	    
	    str(place_order_stop_loss),
	    str(place_order_profit),
	    str(ts),
	    )
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	return True
	#print("sqldata_insert----sql_support_big_amount_strategy_bot--------------------------83",arb_web_input)
	#print("LINE---sqldata_insert----------437")



def sql_clear_order_bot(order_info,own_name,ex_id,api_name,pair,side,price_type,signal,uuid,order_id):
	mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
	mycursor=mysqlconn.cursor()
	now_time = datetime.fromtimestamp(time.time())
	str_time = str(now_time)
	ts = str_time[:-7]
	sql= "insert into clear_order_bot_table(own_name,ex_id,api_name,input_pair,input_side,price_type,input_signal,uuid,order_id,order_status,pair,accu_amount,avg_price,amount,side,price,creation_time,is_using,update_time,timestamp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (
		str(own_name),
		str(ex_id),
		str(api_name),
	    str(pair),
	    str(side),
	    str(price_type),
	    str(signal),
	    str(uuid),
	    str(order_id),
	    str(order_info['order_status']),
	    str(order_info['pair']),
	    str(order_info['accu_amount']),
	    str(order_info['avg_price']),
	    str(order_info['amount']),
	    str(order_info['side']),
	    str(order_info['price']),
	    str(order_info['creation_time']),
	    str(order_info['is_using']),
	    str(order_info['update_time']),
	    str(ts),
	    )
	mycursor.execute(sql,val)
	mysqlconn.commit()
	mycursor.close()
	mysqlconn.close()
	return True
	#print("sqldata_insert----sql_clear_order_bot--------------------------471",arb_web_input)
	#print("LINE---sqldata_insert----------437")
def update_staus_for_orderid(str_orderid,str_order_status):
	try:
		status_mysqlconn=mysql.connector.connect(host = MYSQL_HOST,user = MYSQL_USER,password = MYSQL_PASSWORD,database = MYSQL_DATABASE,auth_plugin = MYSQL_AUTH_PLUGIN,)
		mycursor=status_mysqlconn.cursor()
		mycursor.execute("""update order_details_price_table set status=%s where order_details_price_table.order_id=%s""", (str_order_status, str_orderid))
		status_mysqlconn.commit()
		mycursor.close()				
		return True

	except mysql.connector.Error as error:
		print("Failed to update update_staus_for_orderid {}".format(error))
		
	finally:
		if (status_mysqlconn.is_connected()):
			status_mysqlconn.close()

