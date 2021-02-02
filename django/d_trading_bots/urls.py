"""d_trading_bots URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""




from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from main.views import IndexPageView, ChangeLanguageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('TwoFaCheck/', views.TwoFaCheck, name='TwoFaCheck'),
    path('logs/<path:filename>', views.download, name='download'),
    path('data/<path:filename>', views.download_data, name='download data'),
    path('reports/<path:filename>', views.download_report, name='download_report'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='login.html'), name='logout'),
    path('', views.index, name='home'),
    path('avg-tool/', include('avg_tool.urls')),
    path('support-big-amount-bot/', include('support_big_amount.urls')),
    path('support-trailing-stop-bot/', include('support_trailing_stop.urls')),
    path('atr-trailing-stop-bot/', include('atr_trailing_stop.urls')),
    path('arb-2way-tool/', include('arb_2way.urls')),
    path('atr-trailing-stop-bot-tool/', include('atr_trailing_stop_tool.urls')),
    path('support-multi-box/', include('support_multi_box.urls')),
    path('two_way_sp_tool/', include('two_way_sp.urls')),
    path('bs-sb-continuously-tool/', include('bs_sb_continuously_tool.urls')),
    path('addapiuser/', include("api_key_register.urls") ),
    path('signup/', IndexPageView.as_view(), name='index'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', ChangeLanguageView.as_view(), name='change_language'),
    path('accounts/', include('accounts.urls')),
    path('admin_board/', include('admin_dashboard.urls')),
    path('twoFADash/', include('TwoFA_user.urls')),
    path('admin_all_trade/', include('AdminAllTrade.urls')),
]
urlpatterns += staticfiles_urlpatterns()
