__author__ = 'Anmol'

from rest_framework import serializers
from packets.models import Packet


class PacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packet
        fields = ('pkt_id', 'priority', 'MSG_type', 'time', 'node', 'channel', 'data')
