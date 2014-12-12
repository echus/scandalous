__author__ = 'Anmol'

from django.conf.urls import patterns, url
from packets import views

urlpatterns = [
    url(r'^$', views.AnalyseQuery.as_view()),
]
