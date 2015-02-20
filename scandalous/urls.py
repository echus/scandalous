from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^packets/', include('packets.urls')),
    url(r'^nodes/', include('nodes.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
