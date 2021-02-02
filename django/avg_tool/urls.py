from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:id>', views.index, name='index'),
    path('logs/<path:filename>', views.download, name='download'),
    path('tracking', views.tracking, name='tracking'),
    path('HowToUseAvgTool', views.HowToUseAvgTool, name='HowToUseAvgTool'),
]
