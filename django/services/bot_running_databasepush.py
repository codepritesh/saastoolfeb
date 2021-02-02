
import json
import ast
from pprint import pprint
from admin_dashboard.forms import UserDataForm, UserUpdateForm,UserBotInstancesRunningForm,UserBotInstancesMaxForm
from admin_dashboard.models import UserPermission,UserBotInstancesMax,UserBotInstancesRunning
from django.contrib.auth.models import User



def update_running_bot_to_database():
	with open('services/running_bot_file.txt') as f:
		data = f.read()
	live_running_data = json.loads(data)
	#print("pritesh pritesh pritesh pritesh pritesh: ", type(live_running_data))
	#pprint(live_running_data)
	#print("---------------------------------------- ")
	all_users_running_data = UserBotInstancesRunning.objects.all()
	for user_running in all_users_running_data.iterator():
		fetched_username = user_running.user_name
		pk_fetched_username_id = user_running.user_name.id
		str_username= str(fetched_username)

		Arb2WayBot_counter = 0
		AtrTrailingStopTool_counter = 0
		BSSBContinuouslyTool_counter = 0
		ClearOrderBot_counter = 0
		SupportBigAmountBot_counter = 0
		SupportMultiBoxBot_counter = 0
		SupportTrailingStopBot_counter = 0
		TwoWaySpBot_counter = 0

		for key in live_running_data.keys():
			
			if key == 'Arb2WayBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						Arb2WayBot_counter = Arb2WayBot_counter+1
				

			elif key == 'AtrTrailingStopTool':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						AtrTrailingStopTool_counter = AtrTrailingStopTool_counter+1
				

			elif key == 'BSSBContinuouslyTool':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						BSSBContinuouslyTool_counter = BSSBContinuouslyTool_counter+1
				

			elif key == 'ClearOrderBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						ClearOrderBot_counter = ClearOrderBot_counter+1
				

			elif key == 'SupportBigAmountBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						SupportBigAmountBot_counter = SupportBigAmountBot_counter+1
				
			elif key == 'SupportMultiBoxBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						SupportMultiBoxBot_counter = SupportMultiBoxBot_counter+1
				

			elif key == 'SupportTrailingStopBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						SupportTrailingStopBot_counter = SupportTrailingStopBot_counter+1
				

			elif key == 'TwoWaySpBot':
				for list_running in live_running_data[key]:
					if list_running['own_name'] == str_username:
						TwoWaySpBot_counter = TwoWaySpBot_counter+1
				

			else:
				print("something went wrong in services/bot_running_databasepush.py or no bot running")

		t = UserBotInstancesRunning.objects.get(pk=pk_fetched_username_id)

		t.arb_two_way_bots_running = Arb2WayBot_counter
		t.atr_trailing_stop_bots_running = AtrTrailingStopTool_counter
		t.bs_sb_continuously_tool_bots_running = BSSBContinuouslyTool_counter
		t.avg_tool_bots_running = ClearOrderBot_counter
		t.support_big_amount_bots_running = SupportBigAmountBot_counter
		t.support_multi_box_bots_running = SupportMultiBoxBot_counter
		t.support_trailing_stop_bots_running = SupportTrailingStopBot_counter
		t.two_way_sp_tool_bots_running = TwoWaySpBot_counter
		t.save()





def get_max_bot_running(bot_name,web_input):
	fetched_user = web_input['own_name']
	print(bot_name)
	user_update_data = User.objects.get(username = fetched_user)
	user_id = user_update_data.id

	fetch_number_of_bot_running  = UserBotInstancesRunning.objects.get(pk=user_id)
	fetch_number_of_bot_max_bot  = UserBotInstancesMax.objects.get(pk=user_id)


	if bot_name == "Arb2WayBot":

		max_bot_allowed = fetch_number_of_bot_max_bot.arb_two_way_bots_max
		number_of_bot_running = fetch_number_of_bot_running.arb_two_way_bots_running

	elif bot_name == "AtrTrailingStopTool":
		max_bot_allowed = fetch_number_of_bot_max_bot.atr_trailing_stop_bots_max
		number_of_bot_running = fetch_number_of_bot_running.atr_trailing_stop_bots_running

		

	elif bot_name == "BSSBContinuouslyTool":
		max_bot_allowed = fetch_number_of_bot_max_bot.bs_sb_continuously_bots_max
		number_of_bot_running = fetch_number_of_bot_running.bs_sb_continuously_tool_bots_running
		

	elif bot_name == "ClearOrderBot":
		max_bot_allowed = fetch_number_of_bot_max_bot.avg_tool_bots_max
		number_of_bot_running = fetch_number_of_bot_running.avg_tool_bots_running

	elif bot_name == "SupportBigAmountBot":
		max_bot_allowed = fetch_number_of_bot_max_bot.support_big_amount_bots_max
		number_of_bot_running = fetch_number_of_bot_running.support_big_amount_bots_running

	elif bot_name == "SupportMultiBoxBot":
		max_bot_allowed = fetch_number_of_bot_max_bot.support_multi_box_bots_max
		number_of_bot_running = fetch_number_of_bot_running.support_multi_box_bots_running

	elif bot_name == "SupportTrailingStopBot":
		max_bot_allowed = fetch_number_of_bot_max_bot.support_trailing_stop_bots_max
		number_of_bot_running = fetch_number_of_bot_running.support_trailing_stop_bots_running

	elif bot_name == "TwoWaySpBot":
		max_bot_allowed = fetch_number_of_bot_max_bot.two_way_sp_tool_bots_max
		number_of_bot_running = fetch_number_of_bot_running.two_way_sp_tool_bots_running
	else:
		print("something went wrong in get_max_bot_running services/bot_running_databasepush.py or no bot running")
	print('number_of_bot_running----------------',number_of_bot_running)
	print('max_bot_allowed----------------',max_bot_allowed)

	if number_of_bot_running < max_bot_allowed:
		return True
	else:
		return False








	


