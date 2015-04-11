__author__ = 'Anmol'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from nodes.models import Node
from nodes.models import Channel
from nodes.serializers import NodeSerializer
from nodes.serializers import ChannelSerializer
from packets.models import Packet

import json
import os
from collections import OrderedDict

import logging

NODES_DIR = "/home/user/public_html/scandalous.com/scandal-config/nodes"

logger = logging.getLogger("scandalous.debug")

class ActiveNodes(APIView):
    # Sets Response to prioritise rendering in JSON format
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # Get active nodes
        active_nodes = set(Packet.objects.all().values_list('node'))
        active_nodes = [i[0] for i in active_nodes]

        # Read all node config files
        nodes = []
        for fn in os.listdir(NODES_DIR):
            with open(os.path.join(NODES_DIR, fn)) as node_file:
                for node in json.load(node_file):
                    nodes.append(node)

        # Get list of active node addresses and names
        response = []
        for node in nodes:
            if int(node["address"]) in active_nodes:
                logger.error("In active_nodes")
                n = OrderedDict()
                n["node"] = node["address"]
                n["device"] = node["name"]
                response.append(n)

        return Response(response)

class GetChannels(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, qnode):
        channel_qs = Channel.objects.filter(node=qnode, direction='out')
        serializer = ChannelSerializer(channel_qs, many=True)

        logger.error("channels response")
        logger.error(serializer.data)
        return Response(serializer.data)
