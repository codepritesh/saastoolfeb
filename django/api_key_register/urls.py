from django.urls import path
from . import views
urlpatterns = [
    path('', views.apikey_form,name='apikey_insert'),# get and post request for insert operation
    path('<int:id>', views.apikey_form, name='apikey_update'), #get and post request for update
    path('delete/<int:id>', views.apikey_delete, name='apikey_delete'),
    path('list/', views.apikey_list,name='apikey_list'),  # get request to retrive and display all records
]