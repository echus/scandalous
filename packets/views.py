__author__ = 'Anmol'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from packets.models import Packet
from packets.serializers import PacketSerializer
import datetime
import time
import re


# All url /packet? queries processed here
class AnalyseQuery(APIView):
    # Sets Response to prioritise rendering in JSON format
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # This call pulls any query parameters of the specified string in URL path
        node = request.GET.get('node')
        ch = request.GET.get('ch')

        # Decision statements used to direct URL request to appropriate function
        if (node and ch) is not None:
            return Response(self.filter_node_channel(int(node), int(ch)).data)
        elif node is not None:
            return Response(self.filter_node(int(node)).data)

        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

        if (limit and offset) is not None:
            return Response(self.filter_limit_offset(int(limit), int(offset)).data)
        elif limit is not None:
            return Response(self.filter_latest(int(limit)).data)
        elif offset is not None:
            return Response(self.filter_offset(int(offset)).data)

        tlimit = request.GET.get('tlimit')
        toffset = request.GET.get('toffset')

        if tlimit is not None:
            if re.match(r'h', tlimit) is not None:
                tlimit_dt = datetime.timedelta.strptime(tlimit, '%Hh%Mm%Ss')
            elif re.match(r'm', tlimit) is not None:
                tlimit_dt = datetime.timedelta.strptime(tlimit, '%Mm%Ss')
            else:
                tlimit_dt = datetime.timedelta.strptime(tlimit, '%Ss')

        if toffset is not None:
            if re.match(r'h', toffset) is not None:
                toffset_dt = datetime.timedelta.strptime(toffset, '%Hh%Mm%Ss')
            elif re.match(r'm', toffset) is not None:
                toffset_dt = datetime.timedelta.strptime(toffset, '%Mm%Ss')
            else:
                toffset_dt = datetime.timedelta.strptime(toffset, '%Ss')

        if (tlimit and toffset) is not None:
            return Response(self.filter_time_limit_offset(tlimit_dt, toffset_dt).data)
        elif tlimit is not None:
            return Response(self.filter_time_limit(tlimit_dt).data)
        elif toffset is not None:
            return Response(self.filter_time_offset(toffset_dt).data)

        return Response(self.list_all().data)

    # Filter all packets by node only
    def filter_node(self, url_node):
        packetlist = Packet.objects.filter(node=url_node)
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Filter all packets by node and channel
    def filter_node_channel(self, url_node, url_channel):
        packetlist = Packet.objects.filter(node=url_node, channel=url_channel)
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return latest 'x' packets
    def filter_latest(self, num_packets):
        packetlist = Packet.objects.order_by('-time')[:num_packets]
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return all packets up until specified offset. i.e. If offset = 100, return packets 1->100
    def filter_offset(self, num_offset):
        packetlist = Packet.objects.order_by('-time')[num_offset:]
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return "limit" packets starting from "offset" packet. i.e. If limit = 10, offset = 100, return packets 90->100
    def filter_limit_offset(self, num_limit, num_offset):
        packetlist = Packet.objects.order_by('-time')[num_offset:num_offset+num_limit]
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return all packets made after specified time delta
    def filter_time_limit(self, limit_dt):
        packetlist = Packet.objects.filter(
            time__gte=datetime.datetime.now()-limit_dt)
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return all packets made before specified time delta
    def filter_time_offset(self, offset_dt):
        packetlist = Packet.objects.filter(
            time__lte=datetime.datetime.now()-offset_dt)
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return packets made in time limit specified by tlimit_dt and offset_dt
    def filter_time_limit_offset(self, limit_dt, offset_dt):
        packetlist = Packet.objects.filter(
            time__gte=datetime.datetime.now() - (limit_dt + offset_dt),
            time__lte=datetime.datetime.now() -
            offset_dt)
        serializer = PacketSerializer(packetlist, many=True)
        return serializer

    # Return all packets
    def list_all(self):
        packetlist = Packet.objects.all()
        serializer = PacketSerializer(packetlist, many=True)
        return serializer



