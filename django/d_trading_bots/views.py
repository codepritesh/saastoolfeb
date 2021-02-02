
import os
import sys
import locale
import pyotp

import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + '/../../libs')
sys.path.append(dir_path + '/../bots')
sys.path.append(dir_path + '/../../tools')
sys.path.append(dir_path + '/../../scripts')

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from TwoFA_user.models import User_twofa
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib import messages

locale.setlocale(locale.LC_ALL, '')

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render

@login_required(login_url='/login')
def index(request):
    print(request.COOKIES)
    print("-------------index---------index-------")
    print(request.session.items())
    us = str(request.user)
    context = {'own_name': us}

    user2fa_id = request.user.id

    if User_twofa.objects.filter(pk = user2fa_id).exists():
        print("row exists")
    else:
        User_twofa_row = User_twofa(pk = user2fa_id)
        User_twofa_row.save()

    fetch_User_twofa = User_twofa.objects.get(pk=user2fa_id)
    result_2fa = fetch_User_twofa.two_fa_activated
    if result_2fa == False:
        return render(request, 'home_admin.html', context)
    else:
        key = "twoFAverified"
        if key in request.COOKIES.keys():
            TwoFAverified = request.COOKIES['twoFAverified']
            print("TwoFAverified--------------------------------TwoFAverified------------------TwoFAverified",TwoFAverified)
            if (TwoFAverified == "True"):
                return render(request, 'home_admin.html', context)
            else:
                get_session_from_cookie = request.COOKIES['sessionid']
                response = logout_for2fa(request,get_session_from_cookie,user2fa_id)
                return response
       
        
       
        else:
            get_session_from_cookie = request.COOKIES['sessionid']
            response = logout_for2fa(request,get_session_from_cookie,user2fa_id)
            return response
      
        

def download(request, filename):
    compressed_log = ''
    if compressed_log:
        file_path = f'logs/{compressed_log}'
        content_type = 'application/gzip'
    else:
        file_path = f'logs/{filename}'
        content_type = 'application/octet-stream'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=content_type)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_data(request, filename):
    file_path = 'data/{}'.format(filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_report(request, filename):
    file_path = 'reports/{}'.format(filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
def logout_for2fa(request,get_cookie,user_id):
    response = HttpResponseRedirect('/TwoFaCheck')
    response.set_cookie('bot_session', get_cookie)# this is to store cookie for 2fa
    response.set_cookie('bot_user_id', user_id)
    response.delete_cookie('sessionid')
   # response.delete_cookie('cookie_name2')
    return response


def TwoFaCheck(request):
    if request.method == "GET":
        context = {"data":"data"}
        return render(request, 'twoFAOTPcheck.html', context)


    else:
        user_id = request.COOKIES['bot_user_id']
        print("userid-------------------------------------from cookies",user_id)
        input_password = request.POST['password']
        print("input_password-------------------------------------from post",input_password)

        fetch_User_twofa = User_twofa.objects.get(pk=user_id)
        secreate_key_for_otp = fetch_User_twofa.secret_key_google
        print("secreate_key_for_otp-------------------------------------from_database",secreate_key_for_otp)

        totp=pyotp.TOTP(secreate_key_for_otp)
        print("totp-------------------------------------from_totp",totp)
        verification_status = totp.verify(input_password)
        get_session= request.COOKIES['bot_session'] 
        print("get_session-------------------------------------from_cookies",get_session)



        if verification_status == True:
            print("veryfi--------------------------------------true")
            print(request.COOKIES)
            print("-------------verification_status---------verification_status-------")
            print(request.session.items())
            response = HttpResponseRedirect('/')
            response.set_cookie('sessionid', get_session, max_age = (3600*24))
            response.set_cookie('twoFAverified', verification_status, max_age = 3600)
            return response



        else:
            print("veryfi--------------------------------------flase")
            response = HttpResponseRedirect('/TwoFaCheck')
            messages.error(request, 'wrong otp pls provide correct GA otp or contact to Administrator.')
            return response



    




