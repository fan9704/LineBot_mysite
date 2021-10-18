"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin, auth
from django.conf import settings
from django.contrib.auth.decorators import login_required
# admin.autodiscover()
from django.contrib import auth
from django.urls import path
from django.conf.urls import url
from django.urls.conf import re_path
import mysites.views
from mysites.line import callback
#path(pattern,action)
urlpatterns = [
    path('callback/', callback),
    path('admin/', admin.site.urls),
    url(r'^menu/$',mysites.views.menu),
    url(r'^welcome/$',mysites.views.welcome),
    re_path(r'comment/(?P<id>\d{1,5})/',login_required(mysites.views.comment)),
    path('accounts/login/',mysites.views.sign_in,name='Login'),
    path('accounts/register/',mysites.views.register, name='Register'),
    path('index/', mysites.views.IndexView.as_view()),
    path('', mysites.views.IndexView.as_view()),
    path('accounts/logout/',mysites.views.logout),
    path('firstmenu/', mysites.views.menu, {'id':'1'}),
    path('secondmenu/', mysites.views.menu, {'id':'2'}),
    path('restaurants_list/', mysites.views.list, {'model': mysites.models.Restaurant}),
    path('users_list/',mysites.views.list, {'model': auth.models.User}),
    path('index2/',mysites.views.index)
    
]
if settings.DEBUG:#DEBUG模式開啟後才能用的功能
    urlpatterns += [
        # url(r'^(\w+)/math/(\w+)/$',mysites.views.math), #(\w+))代表接收的參數
    ]
#正規表達式 ^代表配對開始 $代表配對結束
