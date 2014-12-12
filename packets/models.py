__author__ = 'Anmol'

from django.db import models

# Packet MYSQL DB model


class Packet(models.Model):
    time = models.DateTimeField(primary_key=True, auto_now_add=True, blank=True)
    channel = models.IntegerField(default=0)
    node = models.IntegerField(default=0)
    data = models.IntegerField(default=0)

    # Retrieved packet entries will be sorted in descending time order by default.
    class Meta:
        ordering = ('-time',)

