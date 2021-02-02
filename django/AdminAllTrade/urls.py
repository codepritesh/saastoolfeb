from django.urls import path
from . import views
urlpatterns = [
    path('', views.all_bot_index,name='admin_allBot_index'),# get and post request for insert operation
    path('trade_data/', views.user_bot_index, name='user_bot_index'), #get and post request for update
    
    #path('', views.all_bot_search, name='admin_all_bot_search'), #get and post request for update
    #path('delete/<int:id>', views.apikey_delete, name='apikey_delete'),
    #path('list/', views.apikey_list,name='apikey_list'),  # get request to retrive and display all records
]
