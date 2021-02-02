from __future__ import unicode_literals

from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class UserPermission (models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    
    
    avg_tool = models.BooleanField(default=False)

    support_big_amount_bot = models.BooleanField(default=False)

    support_trailing_stop_bot = models.BooleanField(default=False)

    arb_twoway_tool = models.BooleanField(default=False)

    atr_trailing_stop_bot_tool = models.BooleanField(default=False)

    two_way_sp_tool = models.BooleanField(default=False)

    support_multi_box = models.BooleanField(default=False)

    bs_sb_continuously_tool = models.BooleanField(default=False)



    def __str__(self):
        return "%s the username" % self.user_name.username



class UserBotInstancesMax (models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    
    avg_tool_bots_max = models.IntegerField(default=1)

    support_big_amount_bots_max = models.IntegerField(default=1)

    support_trailing_stop_bots_max = models.IntegerField(default=1)

    arb_two_way_bots_max = models.IntegerField(default=1)

    atr_trailing_stop_bots_max = models.IntegerField(default=1)

    two_way_sp_tool_bots_max = models.IntegerField(default=1)

    support_multi_box_bots_max = models.IntegerField(default=1)

    bs_sb_continuously_bots_max= models.IntegerField(default=1)



    def __str__(self):
        return "%s the username" % self.user_name.username



class UserBotInstancesRunning (models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    
    
    avg_tool_bots_running = models.IntegerField(default=0)

    support_big_amount_bots_running  = models.IntegerField(default=0)

    support_trailing_stop_bots_running  = models.IntegerField(default=0)

    arb_two_way_bots_running = models.IntegerField(default=0)

    atr_trailing_stop_bots_running = models.IntegerField(default=0)

    two_way_sp_tool_bots_running  = models.IntegerField(default=0)

    support_multi_box_bots_running = models.IntegerField(default=0)

    bs_sb_continuously_tool_bots_running = models.IntegerField(default=0)



    def __str__(self):
        return "%s the username" % self.user_name.username




    

    
