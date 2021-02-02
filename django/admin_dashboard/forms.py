from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models  import  UserPermission,UserBotInstancesMax,UserBotInstancesRunning





class  UserBotInstancesRunningForm (forms.ModelForm):
  class Meta():
    model = UserBotInstancesRunning
    fields = (         'user_name',
                       'avg_tool_bots_running',
                       'support_big_amount_bots_running',
                       'support_trailing_stop_bots_running',
                       'arb_two_way_bots_running',
                       'atr_trailing_stop_bots_running',
                       'two_way_sp_tool_bots_running',
                       'support_multi_box_bots_running',
                       'bs_sb_continuously_tool_bots_running')     # you can change the tuple element position to show it diffrently.
            
    labels = {  

                 #below label  is for changing labes as showin in forms
                
                'user_name': 'user_name',
                'avg_tool_bots_running':'avg_tool_bots_running',
                'support_big_amount_bots_running': 'support_big_amount_bots_running',
                'support_trailing_stop_bots_running': 'support_trailing_stop_bots_running',
                'arb_two_way_bots_running': 'arb_two_way_bots_running',
                'atr_trailing_stop_bots_running': 'atr_trailing_stop_bots_running',

                'two_way_sp_tool_bots_running':'two_way_sp_tool_bots_running',
                'support_multi_box_bots_running':'support_multi_box_bots_running',
                'bs_sb_continuously_tool_bots_running':'bs_sb_continuously_tool_bots_running',             
                
            }
  
    def __init__(self,*args, **kwargs):
        super(UserBotInstancesRunningForm,self).__init__(*args, **kwargs)
         #below code is for not showing a empty label
        self.fields['user_name'].empty_label = "select"
         #below code is for not showing a mandatory field
        self.fields['user_name'].required = False

class  UserBotInstancesMaxForm (forms.ModelForm):
  class Meta():
    model = UserBotInstancesMax
    fields = ( 
                       'user_name',
                       'avg_tool_bots_max',
                       'support_big_amount_bots_max',
                       'support_trailing_stop_bots_max',
                       'arb_two_way_bots_max',
                       'atr_trailing_stop_bots_max',
                       'two_way_sp_tool_bots_max',
                       'support_multi_box_bots_max',
                       'bs_sb_continuously_bots_max')     # you can change the tuple element position to show it diffrently.
            
    labels = {  

                 #below label  is for changing labes as showin in forms
                
                'user_name': 'user_name',
                'avg_tool_bots_max':'avg_tool_bots_max',
                'support_big_amount_bots_max': 'support_big_amount_bots_max',
                'support_trailing_stop_bots_max': 'support_trailing_stop_bots_max',
                'arb_two_way_bots_max': 'arb_two_way_bots_max',
                'atr_trailing_stop_bots_max': 'atr_trailing_stop_bots_max',

                'two_way_sp_tool_bots_max':'two_way_sp_tool_bots_max',
                'support_multi_box_bots_max':'support_multi_box_bots_max',
                'bs_sb_continuously_bots_max':'bs_sb_continuously_bots_max',             
                
            }
  
    def __init__(self,*args, **kwargs):
        super(UserBotInstancesMaxForm,self).__init__(*args, **kwargs)
         #below code is for not showing a empty label
        self.fields['user_name'].empty_label = "select"
         #below code is for not showing a mandatory field
        self.fields['user_name'].required = False




class  UserDataForm (forms.ModelForm):
  class Meta():
    model = UserPermission
    fields = ( 
                       'user_name',
                       'avg_tool',
                       'support_big_amount_bot',
                       'support_trailing_stop_bot',
                       'arb_twoway_tool',
                       'atr_trailing_stop_bot_tool',
                       'two_way_sp_tool',
                       'support_multi_box',
                       'bs_sb_continuously_tool')     # you can change the tuple element position to show it diffrently.
            
    labels = {  

                 #below label  is for changing labes as showin in forms
                
                'user_name': 'user_name',
                'avg_tool':'avg_tool',
                'support_big_amount_bot': 'support-big-amount-bot',
                'support_trailing_stop_bot': 'support-trailing-stop-bot',
                'arb_twoway_tool': 'arb-twoway-tool',
                'atr_trailing_stop_bot_tool': 'atr-trailing-stop-bot-tool',

                'two_way_sp_tool':'two_way_sp_tool',
                'support_multi_box':'support-multi-box',
                'bs_sb_continuously_tool':'bs-sb-continuously-tool',             
                
            }
  
    def __init__(self,*args, **kwargs):
        super(UserDataForm,self).__init__(*args, **kwargs)
         #below code is for not showing a empty label
        self.fields['user_name'].empty_label = "select"
         #below code is for not showing a mandatory field
        self.fields['user_name'].required = False



class UserUpdateForm(forms.ModelForm):
  class Meta():
    model = User
    fields = ( 
                       'password',
                       'last_login',
                       'is_superuser',
                       'username',
                       'first_name',
                       'last_name',
                       'email',
                       'is_staff',
                       'is_active',
                       'date_joined'
                       )     # you can change the tuple element position to show it diffrently.
            
    labels = {  

                 #below label  is for changing labes as showin in forms
                
                'password': 'password',
                'last_login':'last_login',
                'is_superuser': 'is_superuser',
                'username': 'username',
                'first_name': 'first_name',
                'last_name': 'last_name',

                'email': 'email',

                'is_staff':'is_staff',
                'is_active':'is_active',
                'date_joined':'date_joined',             
                
            }
  
    def __init__(self,*args, **kwargs):
      super(UserUpdateForm,self).__init__(*args, **kwargs)
         #below code is for not showing a empty label
      #self.fields['user_name'].empty_label = "select"
         #below code is for not showing a mandatory field
      self.fields['password'].required = False
      self.fields['last_login'].required = False
      self.fields['is_superuser'].required = False
      self.fields['username'].required = False
      self.fields['first_name'].required = False
      self.fields['last_name'].required = False
      self.fields['email'].required = False
      self.fields['is_staff'].required = False
      self.fields['is_active'].required = False
      self.fields['date_joined'].required = False
      #self.fields['password'].widget = HiddenInput()