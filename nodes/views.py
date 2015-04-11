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
        # TODO check node is active based on heartbeats with timeout

        # Get active nodes
        active_nodes = set(Packet.objects.all().values_list('node'))
        active_nodes = [i[0] for i in active_nodes]

        # Read all Scandal node config files
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
                d = OrderedDict()
                d["node"] = node["address"]
                d["device"] = node["name"]
                response.append(d)

        return Response(response)

class OutChannels(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, qnode):
        # TODO get active channels only?

        # Read channels for qnode from Scandal node config files
        output_channels = []
        for fn in os.listdir(NODES_DIR):
            with open(os.path.join(NODES_DIR, fn)) as node_file:
                for node in json.load(node_file):
                    if int(node["address"]) == int(qnode):
                        output_channels = node["output_channels"]

        # Get list of channel numbers and names
        response = []
        for ch in output_channels:
            d = OrderedDict()
            d["channel"] = ch["channel"]
            d["value"] = ch["name"]
            response.append(d)

        return Response(response)

class InChannels(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, qnode):
        # Read channels for qnode from Scandal node config files
        input_channels = []
        for fn in os.listdir(NODES_DIR):
            with open(os.path.join(NODES_DIR, fn)) as node_file:
                for node in json.load(node_file):
                    if int(node["address"]) == int(qnode):
                        input_channels = node["input_channels"]

        # Get list of channel numbers and names
        response = []
        for ch in input_channels:
            d = OrderedDict()
            d["channel"] = ch["channel"]
            d["value"] = ch["name"]
            response.append(d)

        return Response(response)
