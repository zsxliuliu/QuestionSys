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
from note import views
app_name = 'note'

urlpatterns=[
    url(r'^newnote', views.newNote, name='newnote'),
    url(r'^editnote/(?P<note_id>\d+)$', views.editnote, name='editnote'),
    url(r'^deletenote/(?P<note_id>\d+)$', views.deletenote, name='deletenote'),
    # url(r'^register', views.register, name='register'),
    # url(r'^index', views.index, name='index'),
    # url(r'^usercenter', views.usercenter, name='usercenter'),
    # url(r'^logout', views.logout, name='logout'),


]
