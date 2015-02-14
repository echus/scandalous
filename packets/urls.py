__author__ = 'Anmol'

from django.conf.urls import patterns, url
from packets import views

urlpatterns = [
    url(r'^$', views.AnalyseQuery.as_view()),
    url(r'init', views.Driver.as_view()),
    url(r'outbound', views.Driver.as_view())
]
