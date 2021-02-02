from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:id>', views.index, name='index'),
    path('tracking', views.tracking, name='tracking'),
    path('snapshot', views.snapshot, name='snapshot'),
    path('resume', views.resume_bot, name='resume'),
    path('HowToUseSupportTrailingBot', views.HowToUseSupportTrailingBot, name='HowToUseSupportTrailingBot'),
]
