from django.urls import path
from . import views

urlpatterns = [
    path('', views.twoFADash_index, name='twoFADash'),
     path('twofa/', views.twoFAgoogle_index, name='twoFAgoogle'),
     path('2FAactivatePage/', views.twoFAGActivatePage, name='twoFAGActivatePage'),
    #path('send_message_for_activation/', views.send_message_for_activation, name='send_message_for_activation'),
    
       
]