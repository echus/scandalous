__author__ = 'Anmol'

from django.conf.urls import patterns, url
from nodes import views

urlpatterns = [
    url(r'^$', views.ActiveNodes.as_view()),
    url(r'(\d+)/channels', views.OutChannels.as_view()),
    url(r'(\d+)/inchannels', views.InChannels.as_view())
]
