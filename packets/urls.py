__author__ = 'Anmol'

from django.conf.urls import patterns, url
from packets import views

urlpatterns = [
    url(r'^$', views.AnalyseQuery.as_view()),
    url(r'init', views.Driver.as_view(switch=0)),
    url(r'outbound', views.Driver.as_view()),
    url(r'stop', views.Driver.as_view(switch=1)),
    url(r'backup', views.Driver.as_view(switch=2)),
    url(r'flush', views.Driver.as_view(switch=3))
]
