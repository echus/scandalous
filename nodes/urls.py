__author__ = 'Anmol'

from django.conf.urls import patterns, url
from nodes import views

urlpatterns = [
    url(r'^$', views.ActiveNodes.as_view()),
    url(r'(\d{2})/channels', views.GetChannels.as_view())
]
