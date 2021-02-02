from __future__ import unicode_literals

from django_better_admin_arrayfield.models.fields import ArrayField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings


class User_twofa (models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    countrycode = models.TextField(default="na")
    mobile_number = models.TextField(default="na")
    secret_key_otp = models.TextField(default="na")
    secret_key_google = models.TextField(default="na")
    two_fa_activated = models.BooleanField(default=False)





    def __str__(self):
        return "%s the username" % self.user_name.username
