"""questAnswerSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import  url
from django.contrib.auth.decorators import login_required
from adminuser import views
app_name = 'adminuser'

urlpatterns=[
    url(r'^adminlogin', views.adminLogin, name='adminlogin'),
    url(r'^adminIndex', views.adminIndex, name='adminIndex'),
    url(r'^search', views.knowledgebase, name='search'),
    url(r'^welcome', views.welcome, name='welcome'),
    url(r'^addentity', views.addEntity, name='addentity'),
    url(r'^changentity', views.changeEntity, name='changentity'),
    url(r'^deletentity', views.deleteEntity, name='deletentity'),
    url(r'^addrelation', views.addRelation, name='addrelation'),
    url(r'^changerelation', views.changeRelation, name='changerelation'),
    url(r'^deleterelation', views.deleteRelation, name='deleterelation'),
    url(r'^userlist', views.userList, name='userlist'),
    url(r'^admininfo', views.adminInfo, name='admininfo'),
    url(r'^deleteuser/(?P<user_id>\d+)$', views.deleteuser, name='deleteuser'),
    url(r'^adminlogout', views.adminlogout, name='adminlogout'),

]
