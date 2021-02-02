from django.shortcuts import render, redirect


from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .forms import UserDataForm, UserUpdateForm,UserBotInstancesRunningForm,UserBotInstancesMaxForm
from .models import UserPermission,UserBotInstancesMax,UserBotInstancesRunning
import json
from TwoFA_user.models import User_twofa




@login_required(login_url='/login')
def user_permission_list(request):
    context = {'permission_list' : UserPermission.objects.all()}
    return render(request,"admin_dashboard/all_user_permission_list.html", context)


@login_required(login_url='/login')
def all_user_list(request):
    #us = request.user.id
    #context = {'apikey_list' : APIKEY.objects.all()}

    User = get_user_model()
    all_users = User.objects.all()
    context = {'user_list' : all_users }
    return render(request,"admin_dashboard/dash_board_home.html", context)

@login_required(login_url='/login')
def user_data_update(request,id=0):
    if request.method == "GET":
        if id == 0:
            user_update_form= UserUpdateForm()
            print("user_update_form_update if")
        else:
            user_update_data = User.objects.get(pk=id)
            user_update_form = UserUpdateForm(instance = user_update_data )
            print("user_permision_update else")


        #this below 4 lines capture username and add it to dictionary of context
        context = {"user_update_form":user_update_form}
        #return render(request,"admin_dashboard/user_app_permision_form.html", context )
        return render(request,"admin_dashboard/user_app_data_form.html", context )


    else:
        if id == 0:
            user_update_form = UserUpdateForm(request.POST)
            print("post 1if")

        else:
            user_update_data= User.objects.get(pk=id)
            user_update_form = UserUpdateForm(request.POST, user_update_data)
            user_update_data.delete()
            
            
            




        if user_update_form.is_valid():
            user_update_form.save()

            print("user formsaved")

            if UserPermission.objects.filter(pk=id+1).exists():
                print ("user permision row exists")
            else:
                print ("user permision row not exists")
                book = UserPermission(pk=id+1)
                book.save()
        else:
            print (user_update_form.errors)
            print("form not saved")
        
        return redirect('/admin_board/')
    

    








@login_required(login_url='/login')
def user_delete(request,id=0):
    #us = request.user.id
    #context = {'apikey_list' : APIKEY.objects.all()}

    User = get_user_model()
    selected_user = User.objects.get(pk=id)
    selected_user.delete()
    
    return redirect('/admin_board/')


@login_required(login_url='/login')
def user_permission_update(request,id=0):
    if request.method == "GET":
        if id == 0:
            user_data_form= UserDataForm()
            
        else:
            if UserPermission.objects.filter(pk=id).exists():
                user_permission_form = UserPermission.objects.get(pk=id)
                user_data_form = UserDataForm(instance = user_permission_form )
                
            else:
                print ("not exits")
                book = UserPermission(pk=id)
                book.save()
                user_permission_form = UserPermission.objects.get(pk=id)
                user_data_form = UserDataForm(instance = user_permission_form )
                
            


        #this below 4 lines capture username and add it to dictionary of context

        context = {"user_data_form":user_data_form}
        
        return render(request,"admin_dashboard/user_app_permision_form.html", context )


    else:
        if id == 0:
            user_data_form = UserDataForm(request.POST)
            print("51")
            
        else:
           
            user_permission_form = UserPermission.objects.get(pk=id)
            user_data_form = UserDataForm(request.POST, user_permission_form)
            user_permission_form.delete()

            print("59 form data deleted")
        if user_data_form.is_valid():
            print("63valid adn for created and saved")
            user_data_form.save()
        else:
            print(user_data_form.errors) 


        if UserBotInstancesMax.objects.filter(pk = id).exists():
            print("bot instance exists")
        else:
            UserBotInstancesMax_row = UserBotInstancesMax(pk = id)
            UserBotInstancesMax_row.save()
        #bot max row create 

        if UserBotInstancesRunning.objects.filter(pk = id).exists():
            print("bot instance exists")
        else:
            UserBotInstancesRunning_row = UserBotInstancesRunning(pk = id)
            UserBotInstancesRunning_row.save()
        
        
        return redirect('/admin_board/')



@login_required(login_url='/login')
def user_permission_delete(request,id):
    user_permission_form = UserPermission.objects.get(pk=id)
    user_permission_form.delete()
    return redirect('/admin_board/list/')


@login_required(login_url='/login')
def user_bot_instances_index(request):
    context = {'permission_list' : UserBotInstancesMax.objects.all()}
    return render(request,"admin_dashboard/all_user_bot_instances.html", context)






@login_required(login_url='/login')
def user_bot_instance_max_update(request,id=0):
    if request.method == "GET":
        if id == 0:
            context_form_data= UserBotInstancesMaxForm()
            
        else:
            if UserBotInstancesMax.objects.filter(pk=id).exists():
                UserBotInstancesMax_form = UserBotInstancesMax.objects.get(pk=id)
                context_form_data = UserBotInstancesMaxForm(instance = UserBotInstancesMax_form )
                
            else:
                print ("not exits")
                create_one = UserBotInstancesMax(pk=id)
                create_one.save()
                UserBotInstancesMax_form = UserBotInstancesMax.objects.get(pk=id)
                context_form_data = UserBotInstancesMaxForm(instance = UserBotInstancesMax_form )
                
            


        #this below 4 lines capture username and add it to dictionary of context

        context = {"user_data_form":context_form_data}
        
        return render(request,"admin_dashboard/UserBotInstancesMaxForm.html", context )


    else:
        if id == 0:
            user_data_form = UserBotInstancesMaxForm(request.POST)
            print("209")
            
        else:
           
            UserBotInstancesMax_form = UserBotInstancesMax.objects.get(pk=id)
            user_data_form = UserBotInstancesMaxForm(request.POST, UserBotInstancesMax_form)
            UserBotInstancesMax_form.delete()

            print("59 form data deleted")

            
        if user_data_form.is_valid():
            print("63valid adn for created and saved")
            user_data_form.save()
        else:
            print(user_data_form.errors)

        
        
        return redirect('/admin_board/user_bot_instances_index/')





@login_required(login_url='/login')
def user_bot_running_index(request):
    context = {'permission_list' : UserBotInstancesRunning.objects.all()}
    return render(request,"admin_dashboard/all_user_running_bot_instances.html", context)




@login_required(login_url='/login')
def admin_want_to_kill_userbot(request,id=0):
    user_update_data = User.objects.get(pk=id)
    #print(vars(user_update_data))
    str_username = user_update_data.username
    with open('services/running_bot_file.txt') as f:
        data = f.read()
    live_running_data = json.loads(data)
    catch_user_bot=[]
    for key in live_running_data.keys():
            
            if key == 'Arb2WayBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "arb-2way-tool"

                        catch_user_bot. append(list_running)
                

            elif key == 'AtrTrailingStopTool':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "atr-trailing-stop-bot-tool"
                        catch_user_bot. append(list_running)
                

            elif key == 'BSSBContinuouslyTool':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "bs-sb-continuously-tool"
                        catch_user_bot. append(list_running)
                

            elif key == 'ClearOrderBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "avg-tool"
                        catch_user_bot. append(list_running)
                

            elif key == 'SupportBigAmountBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "support-big-amount-bot"
                        catch_user_bot. append(list_running)
                
            elif key == 'SupportMultiBoxBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "support-multi-box"
                        catch_user_bot. append(list_running)
                

            elif key == 'SupportTrailingStopBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "support-trailing-stop-bot"
                        catch_user_bot. append(list_running)
                

            elif key == 'TwoWaySpBot':
                for list_running in live_running_data[key]:
                    if list_running['own_name'] == str_username:
                        list_running['bot_alias'] = "two_way_sp_tool"
                        catch_user_bot. append(list_running)
                

            else:
                print("something went wrong in services/bot_running_databasepush.py or no bot running")





    context = {'user_list' : catch_user_bot }

    print(catch_user_bot)

    return render(request,"admin_dashboard/admin_want_to_kill_userbot.html", context)


@login_required(login_url='/login')
def user_twofa_dashboard(request,id=0):
    if request.method == "GET":
        all_users = User_twofa.objects.all()
        context = {'user_list' : all_users }
        return render(request,"admin_dashboard/twoFA_allUserhome.html", context)
    else:

        twoFA_user = User_twofa.objects.get(pk=id)
        twoFA_user.secret_key_google = 'na'

        twoFA_user.two_fa_activated = False
        twoFA_user.save()
        return redirect('/admin_board/user_twofa_dashboard/')







        


        


    