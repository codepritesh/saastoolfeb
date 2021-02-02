import os
import sys
from django.contrib import messages

from django.http import HttpResponse, Http404

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + '/../../repositories')
sys.path.append(dir_path + '/../services')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from user_repository_psql import UserRepositoryPSQL
from .consumers import AvgToolConsumer
users_repository = UserRepositoryPSQL()
from base_service import BaseService
from user_permission import User_permission
from admin_dashboard.models import UserPermission,UserBotInstancesRunning,UserBotInstancesMax
from pprint import pprint

# Create your views here.
@login_required
def index(request, id=None):
    us = str(request.user)
    apis = users_repository.list_name_api_key(us)
    if not apis:
        messages.warning(request, ('You have not added any api keys please add api keys'))

        return redirect('home')



        #html = "<html><body><h3>Could not fetch apis for user: %s</h3>\
         #       <h3>Please logout and re-login with another user.</h3></body></html>" % us.upper()
        #return HttpResponse(html)
    options_side = [{'key': 'BUY', 'value': 'buy'}, {'key': 'SELL', 'value': 'sell'}]
    options_price = [{'key': 'Market', 'value': 'price_market'}, {'key': 'Limit', 'value': 'price_limit'}]
    context = {'apis': apis, 'user': us, 'bot_alias': AvgToolConsumer.BOT_ALIAS,
               'options_side': options_side, 'options_price': options_price, 'ws_define': 'avg_tool'}
    if id:
        base_srv = BaseService()
        bot_alias = AvgToolConsumer.BOT_ALIAS
        data = base_srv.fetch_detail(bot_alias, str(id))
        if data:
            apis = [data.get('api_name')]
            context.update({'apis': apis, 'id': id, 'user': us, 'data': data, 'bot_alias': AvgToolConsumer.BOT_ALIAS,
                       'options_side': options_side, 'options_price': options_price})

    #if a user is first lime logging in then to createa database of permision 
    user_id = request.user.id  

    if UserPermission.objects.filter(pk = user_id).exists():
        print("row exists")
    else:
        
        user_permission_row = UserPermission(pk = user_id)
        user_permission_row.save()
     #/if a user is first lime logging in then to createa database of permision 

      
    obj_user_permision = User_permission(user_id)
    user_permission_data = obj_user_permision.check_permission(user_id)

   
    
   
    if user_permission_data.avg_tool:
        try:
            UserBotInstancesRunning_form = UserBotInstancesRunning.objects.get(pk=user_id)
            bot_one = UserBotInstancesRunning_form.avg_tool_bots_running
            bot_two = UserBotInstancesRunning_form.support_big_amount_bots_running
            bot_three = UserBotInstancesRunning_form.support_trailing_stop_bots_running
            bot_four = UserBotInstancesRunning_form.arb_two_way_bots_running
            bot_five = UserBotInstancesRunning_form.atr_trailing_stop_bots_running
            bot_six = UserBotInstancesRunning_form.two_way_sp_tool_bots_running
            bot_seven = UserBotInstancesRunning_form.support_multi_box_bots_running
            bot_eight = UserBotInstancesRunning_form.bs_sb_continuously_tool_bots_running

            another_dict = {"bot_one":bot_one,"bot_two":bot_two,"bot_three":bot_three,"bot_four":bot_four,"bot_five":bot_five,"bot_six":bot_six,"bot_seven":bot_seven,"bot_eight":bot_eight}


        except:
            another_dict={"no_data":"no_data"}
            print("something  went wromng in fileline-85 avgtool/views.py ")
      


        context = {**context, **another_dict}


        try:
            UserBotInstancesMax_data = UserBotInstancesMax.objects.get(pk=user_id)
            max_bot_one = UserBotInstancesMax_data.avg_tool_bots_max
            max_bot_two = UserBotInstancesMax_data.support_big_amount_bots_max
            max_bot_three = UserBotInstancesMax_data.support_trailing_stop_bots_max
            max_bot_four = UserBotInstancesMax_data.arb_two_way_bots_max
            max_bot_five = UserBotInstancesMax_data.atr_trailing_stop_bots_max
            max_bot_six = UserBotInstancesMax_data.two_way_sp_tool_bots_max
            max_bot_seven = UserBotInstancesMax_data.support_multi_box_bots_max
            max_bot_eight = UserBotInstancesMax_data.bs_sb_continuously_bots_max

            max_bot_dict = {"max_bot_one":max_bot_one,"max_bot_two":max_bot_two,"max_bot_three":max_bot_three,"max_bot_four":max_bot_four,"max_bot_five":max_bot_five,"max_bot_six":max_bot_six,"max_bot_seven":max_bot_seven,"max_bot_eight":max_bot_eight}


        except:
            max_bot_dict={"max_no_data":"no_data"}
            print("something  went wromng in max_bot_dict-107 avgtool/views.py ")



        context = {**context, **max_bot_dict}

        return render(request, 'tool/avg_tool.html', context)
    else:
        messages.error(request, ('You are not allowed to see cancel and average tool please subscribe'))

        return redirect('home')
        



@login_required()
def tracking(request):
    base_srv = BaseService()
    tracking_user = str(request.user)
    data = {'tracking_user':tracking_user,'srv_id': base_srv.srv_id,'bot_alias': AvgToolConsumer.BOT_ALIAS,'suff_ws':'avg_tool',
            'bot_name': 'TOOL SUPPORT AVG, CLEAR, CANCEL ORDER','title': 'TOOL SUPPORT AVG, CLEAR, CANCEL ORDER',
            'bot_url': 'avg-tool'}


    try:
        user_id = request.user.id
        UserBotInstancesRunning_form = UserBotInstancesRunning.objects.get(pk=user_id)
        bot_one = UserBotInstancesRunning_form.avg_tool_bots_running
        bot_two = UserBotInstancesRunning_form.support_big_amount_bots_running
        bot_three = UserBotInstancesRunning_form.support_trailing_stop_bots_running
        bot_four = UserBotInstancesRunning_form.arb_two_way_bots_running
        bot_five = UserBotInstancesRunning_form.atr_trailing_stop_bots_running
        bot_six = UserBotInstancesRunning_form.two_way_sp_tool_bots_running
        bot_seven = UserBotInstancesRunning_form.support_multi_box_bots_running
        bot_eight = UserBotInstancesRunning_form.bs_sb_continuously_tool_bots_running

        another_dict = {"bot_one":bot_one,"bot_two":bot_two,"bot_three":bot_three,"bot_four":bot_four,"bot_five":bot_five,"bot_six":bot_six,"bot_seven":bot_seven,"bot_eight":bot_eight}


    except:
        another_dict={"no_data":"no_data"}
        print("something  went wromng in file avgtool/views.py ")
  


    data = {**data, **another_dict}

    return render(request, 'tracking_simple_v1.html', data)

@login_required(login_url='/login/')
def download(request, filename):
    file_path = 'logs/{}'.format(filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

@login_required()
def HowToUseAvgTool(request):
    data = {"usage":"data"}
    return render(request, 'tool/how_to_use_Avg_tool.html', data)
