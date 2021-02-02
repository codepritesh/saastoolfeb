import os
import sys
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render,redirect
from django.contrib import messages

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + '/../../repositories')
sys.path.append(dir_path + '/../services')
sys.path.append(dir_path + '/../helper')
from user_repository_psql import UserRepositoryPSQL
from .consumers import SupportBigAmountConsumer
from fetch_snapshot import *
from user_permission import User_permission
from admin_dashboard.models import UserPermission,UserBotInstancesRunning,UserBotInstancesMax
users_repository = UserRepositoryPSQL()


# Create your views here.
@login_required
def index(request, id=''):
    us = str(request.user)
    apis = users_repository.list_name_api_key(us)
    if not apis:
        messages.warning(request, ('You have not added any api keys please add API key.'))

        return redirect('home')

    context = {'apis': apis, 'user': us, 'bot_alias': SupportBigAmountConsumer.BOT_ALIAS, 'ws_define': 'support_big_amount',
               'type_stop_loss': [{'key': 'Market', 'value': 'market'}, {'key': 'Limit', 'value': 'limit'}]}
    if id:
        base_srv = BaseService()
        bot_alias = SupportBigAmountConsumer.BOT_ALIAS
        data = base_srv.fetch_detail(bot_alias, str(id))
        if data:
            apis = [data.get('api_name')]
            context.update({'apis': apis, 'id': id, 'user': us, 'data': data, 'bot_alias': SupportBigAmountConsumer.BOT_ALIAS})
   #if a user is first time logging in then to createa database of permision 
    user_id = request.user.id  

    if UserPermission.objects.filter(pk = user_id).exists():
        print("row exists")
    else:
        
        user_permission_row = UserPermission(pk = user_id)
        user_permission_row.save()
     #/if a user is first lime logging in then to createa database of permision 
    
    
    obj_user_permision = User_permission(user_id)
    user_permission_data = obj_user_permision.check_permission(user_id)

     

    
    if user_permission_data.support_big_amount_bot:
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
            print("something  went wromng in file avgtool/views.py ")
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
            print("something  went wromng in max_bot_dict")
        context = {**context, **max_bot_dict} 
        return render(request, 'support_big_amount/index.html', context)
    else:
        messages.error(request, ('You are not allowed to see support_big_amount_bot page please subscribe'))

        return redirect('home')


@login_required(login_url='/login/')
def tracking(request):
    base_srv = BaseService()
    tracking_user = str(request.user)
    data = {'tracking_user':tracking_user,'srv_id': base_srv.srv_id, 'bot_alias': SupportBigAmountConsumer.BOT_ALIAS, 'suff_ws': 'support_big_amount',
            'bot_name': 'Support Big Amount Bot', 'title': 'Support Big Amount Bot', 'bot_url': 'support-big-amount-bot'}
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
def resume_bot(request):
    us = str(request.user)
    uuid = request.GET.get('id')
    if not uuid:
        html = '<h1>UUID must include in url</h1>'
        return HttpResponse(html)
    # repository
    port = request.META['SERVER_PORT']
    data = fetch_snapshot_bot_detail(uuid, us, port, SupportBigAmountConsumer.BOT_ALIAS)
    if not data:
        html = '<h1>Bot running or not found snapshot</h1>'
        return HttpResponse(html)
    context = {'apis': [data['api_name']], 'user': us, 'id': uuid, 'data': data, 'resume': True,
               'bot_alias': SupportBigAmountConsumer.BOT_ALIAS, 'ws_define': 'support_big_amount'}
    return render(request, 'support_big_amount/index.html', context)

@login_required()
def HowToUseSupportBigAmountBot(request):
    data = {"usage":"data"}
    return render(request, 'support_big_amount/how_to_use_SupportBigAmount_tool.html', data)


def snapshot(request):
    us = str(request.user)
    base_srv = BaseService()
    port = request.META['SERVER_PORT']
    list_bot_snapshot = fetch_snap_shot_bot(us, port, SupportBigAmountConsumer.BOT_ALIAS)
    data = {'srv_id': base_srv.srv_id, 'bot_alias': SupportBigAmountConsumer.BOT_ALIAS, 'suff_ws': 'support_big_amount',
            'bot_name': 'Support Big Amount Bot', 'title': 'Support Big Amount Bot', 'bot_url': 'support-big-amount-bot', 'list_bot_snapshot': list_bot_snapshot}
    return render(request, 'snapshot_simple.html', data)
