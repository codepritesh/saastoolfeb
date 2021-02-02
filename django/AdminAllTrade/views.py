from django.shortcuts import render, redirect
#from .forms import ApiKeyForm
from django.contrib.auth.models import User
from setup_apikey.models import APIKEY
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from .searchdata import *  #
from datetime import date,timedelta 




# Create your views here.
@permission_required('poll.change_poll')
@login_required(login_url='/login')
def all_bot_index(request):
	today = date.today()
	trade_now_day= today.strftime("%Y-%m-%d")
	trade_yesterday = (today - timedelta(days = 2)).strftime("%Y-%m-%d")
	input_user_name= "all_user"
	input_bot_name= "all_bot"


	input_trade_start= trade_yesterday
	input_trade_end= trade_now_day


	if request.method=="POST":

		input_user_name=request.POST.get("user_name")
		
		input_bot_name=request.POST.get("bot_name")
		
		input_trade_start=request.POST.get("trade_start")
		
		input_trade_end=request.POST.get("trade_end")
		if input_user_name == "all_user":
			if input_bot_name == "all_bot":
				recived_search_data=get_all_user_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
			else:
				recived_search_data=get_all_user_single_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
		else:
			if input_bot_name == "all_bot":
				recived_search_data=get_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
			else:
				recived_search_data=get_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)

		users = User.objects.values()
		userdict={}
		i=1
		for username in users:
			userdict[i]=username['username']
			i=i+1



		context={"recived_data":recived_search_data,"User_Name":userdict,"found_data":number_of_fetched_data,"input_user_name":input_user_name,"input_bot_name":input_bot_name,"input_trade_start":input_trade_start,"input_trade_end":input_trade_end}
		return render(request,"Admin_All_Trade/index.html", context)

	else:

		users = User.objects.values()
		userdict={}
		i=1
		for username in users:
			userdict[i]=username['username']
			i=i+1

		
		context={"User_Name":userdict,"input_user_name":input_user_name,"input_bot_name":input_bot_name,"input_trade_start":input_trade_start,"input_trade_end":input_trade_end}
		return render(request,"Admin_All_Trade/index.html", context)





@login_required(login_url='/login')
def user_bot_index(request):
	today = date.today()
	trade_now_day= today.strftime("%Y-%m-%d")
	trade_yesterday = (today - timedelta(days = 2)).strftime("%Y-%m-%d")
	input_user_name= str(request.user)
	input_bot_name= "all_bot"


	input_trade_start= trade_yesterday
	input_trade_end= trade_now_day


	if request.method=="POST":

		input_user_name=str(request.user)
		
		input_bot_name=request.POST.get("bot_name")
		
		input_trade_start=request.POST.get("trade_start")
		
		input_trade_end=request.POST.get("trade_end")
		if input_user_name == "all_userssss":
			if input_bot_name == "all_bot":
				recived_search_data=get_all_user_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
			else:
				recived_search_data=get_all_user_single_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
		else:
			if input_bot_name == "all_bot":
				recived_search_data=get_all_bot_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)
			else:
				recived_search_data=get_search_data(input_user_name,input_bot_name,input_trade_start,input_trade_end)
				number_of_fetched_data=len(recived_search_data)

		users = str(request.user)
		userdict={1:users}
		



		context={"recived_data":recived_search_data,"User_Name":userdict,"found_data":number_of_fetched_data,"input_user_name":input_user_name,"input_bot_name":input_bot_name,"input_trade_start":input_trade_start,"input_trade_end":input_trade_end}
		return render(request,"Admin_All_Trade/user_index.html", context)

	else:

		users = str(request.user)
		userdict={1:users}

		
		context={"User_Name":userdict,"input_user_name":input_user_name,"input_bot_name":input_bot_name,"input_trade_start":input_trade_start,"input_trade_end":input_trade_end}
		return render(request,"Admin_All_Trade/user_index.html", context)



