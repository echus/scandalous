__author__ = 'Anmol'

from rest_framework import serializers
from nodes.models import Node
from nodes.models import Channel


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('node', 'device')


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('channel', 'value')
