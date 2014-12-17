__author__ = 'Anmol'

from django.db import models

# Packet MYSQL DB model


class Packet(models.Model):
    pkt_id = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    channel = models.IntegerField(default=0)
    node = models.IntegerField(default=0)
    data = models.IntegerField(default=0)

    # Retrieved packet entries will be sorted in descending time order by default.
    class Meta:
        ordering = ('-pkt_id',)

