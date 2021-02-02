from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_user_list, name='admin_dashboard_index'),
    path('<int:id>', views.user_permission_update, name='user_permission_update'),
    path('list/', views.user_permission_list, name='user_permission_list'),
    path('add/<int:id>', views.user_permission_update, name='user_permission_add'),
    path('update_user/<int:id>', views.user_data_update, name='user_data_update'),
    
    path('delete/<int:id>', views.user_delete, name='user_delete'),
    path('delete_user_permision/<int:id>', views.user_permission_delete, name='user_permission_delete'),
    path('user_bot_instances_index/', views.user_bot_instances_index, name='user_bot_instances_index'),
    path('user_bot_instance_max_update/<int:id>', views.user_bot_instance_max_update, name='user_bot_instance_max_update'),
    path('user_bot_running_index/', views.user_bot_running_index, name='user_bot_running_index'),
    path('admin_userbot_dashboard/<int:id>', views.admin_want_to_kill_userbot, name='admin_want_to_kill_userbot'),
    path('user_twofa_dashboard/', views.user_twofa_dashboard, name='user_twofa_dashboard'),
    path('user_twofa_dashboard/<int:id>', views.user_twofa_dashboard, name='admin_want_to_disable2FA'),
    #path('tracking', views.tracking, name='tracking'),
    #path('snapshot', views.snapshot, name='snapshot'),
    #path('resume', views.resume_bot, name='resume'),
    #path('chart', views.plot_chart, name='chart'),

    
]
