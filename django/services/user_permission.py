from django.shortcuts import render, redirect


from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from admin_dashboard.forms import UserDataForm
from admin_dashboard.models import UserPermission





class User_permission:
    def __init__(self, v0):
        self.v0 = v0
        

    
    def check_permission(self,id):
    	user_permission_form = UserPermission.objects.get(pk=id)
    	#user_data_form = UserDataForm(instance = user_permission_form )
    	return user_permission_form

