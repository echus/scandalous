__author__ = 'Anmol'

from django.contrib import admin
from nodes.models import Node, Channel

admin.site.register(Node)
admin.site.register(Channel)
