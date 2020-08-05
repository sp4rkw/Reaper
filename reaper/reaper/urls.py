"""reaper URL Configuration

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
from django.urls import path
from app1 import views as app1_view  # new
 
urlpatterns = [
    path("", app1_view.index),  # new
    path("index.html", app1_view.index),  # new
    path("queryweb", app1_view.queryweb),  # new
    path("querytask", app1_view.querytask),
    path("xraypocgenerate", app1_view.xraypocgenerate),  # new
    path("newawvs", app1_view.newawvs),  # new
    path("newfullscan", app1_view.newfullscan),  # new
    path("deletefullscan", app1_view.deletefullscan),  # new
    path("queryrecord", app1_view.queryrecord),  # new
    # path("newportscan", app1_view.newportscan),  # new
    # path('admin/', admin.site.urls),  # 拒绝django后台
]