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


class ActiveNodes(APIView):
    # Sets Response to prioritise rendering in JSON format
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # List of ALL CAN node addresses, reduce to only active nodes by elimination
        node_list = [10, 20, 30, 31, 40, 41, 50, 60, 70, 80, 81]
        active_nodes = []
        packets = Packet.objects.all()

        for curr_node in node_list:
            if packets.filter(node=curr_node).exists():
                active_nodes.append(curr_node)

        nodes_qs = Node.objects.filter(node__in=active_nodes)
        serializer = NodeSerializer(nodes_qs, many=True)
        return Response(serializer.data)


class GetChannels(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, qnode):
        channel_qs = Channel.objects.filter(node=qnode, direction='out')
        serializer = ChannelSerializer(channel_qs, many=True)
        return Response(serializer.data)





