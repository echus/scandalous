__author__ = 'Anmol'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from packets.models import Packet
from packets.serializers import PacketSerializer
from packets import can
import json
import datetime
import re


# All url /packet? queries processed here
class AnalyseQuery(APIView):
    # Sets Response to prioritise rendering in JSON format
    renderer_classes = [JSONRenderer]

    def get(self, request):
        # This call pulls any query parameters of the specified string in URL path
        node = request.GET.get('node')
        ch = request.GET.get('ch')

        currQS = self.list_all()

        # Decision statements used to direct URL request to appropriate function
        if (node and ch) is not None:
            currQS = self.filter_node_channel(int(node), int(ch), currQS)
        elif node is not None:
            currQS = self.filter_node(int(node), currQS)

        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

        if (limit and offset) is not None:
            currQS = self.filter_limit_offset(int(limit), int(offset), currQS)
        elif limit is not None:
            currQS = self.filter_latest(int(limit), currQS)
        elif offset is not None:
            currQS = self.filter_offset(int(offset), currQS)

        tlimit = request.GET.get('tlimit')
        toffset = request.GET.get('toffset')

        if tlimit is not None:
            tlimit_dt = self.parse_time_delta(tlimit)

        if toffset is not None:
            toffset_dt = self.parse_time_delta(toffset)

        if (tlimit and toffset) is not None:
            currQS = self.filter_time_limit_offset(tlimit_dt, toffset_dt)
        elif tlimit is not None:
            currQS = self.filter_time_limit(tlimit_dt, currQS)
        elif toffset is not None:
            currQS = self.filter_time_offset(toffset_dt, currQS)

        serializer = PacketSerializer(currQS, many=True)
        return Response(serializer.data)


    # Filter all packets by node only
    def filter_node(self, url_node, currQS):
        packetlist = currQS.filter(node=url_node)
        return packetlist

    # Filter all packets by node and channel
    def filter_node_channel(self, url_node, url_channel, currQS):
        packetlist = currQS.filter(node=url_node, channel=url_channel)
        return packetlist

    # Return latest 'x' packets
    def filter_latest(self, num_packets, currQS):
        packetlist = currQS.order_by('-pkt_id')[:num_packets]
        return packetlist

    # Return all packets up until specified offset. i.e. If offset = 100, return packets 1->100
    def filter_offset(self, num_offset, currQS):
        packetlist = reversed(currQS.order_by('pkt_id')[:num_offset])
        return packetlist

    # Return "limit" packets starting from "offset" packet. i.e. If limit = 10, offset = 100, return packets 90->100
    def filter_limit_offset(self, num_limit, num_offset, currQS):
        packetlist = reversed(currQS.order_by('pkt_id')[num_offset-num_limit:num_offset])
        return packetlist

    # Return all packets made after specified time delta
    def filter_time_limit(self, limit_dt, currQS):
        packetlist = currQS.filter(
            time__gte=datetime.datetime.now()-limit_dt)
        return packetlist

    # Return all packets made before specified time delta
    def filter_time_offset(self, offset_dt, currQS):
        packetlist = currQS.filter(
            time__lte=datetime.datetime.now()-offset_dt)
        return packetlist

    # Return packets made in time limit specified by tlimit_dt and offset_dt
    def filter_time_limit_offset(self, limit_dt, offset_dt, currQS):
        packetlist = currQS.filter(
            time__gte=datetime.datetime.now() - (limit_dt + offset_dt),
            time__lte=datetime.datetime.now() -
            offset_dt)
        return packetlist

    # Return all packets
    def list_all(self):
        packetlist = Packet.objects.all()
        return packetlist

    def parse_time_delta(self, s):
        if s is None:
            return None
        d = re.match(r'(?:(?P<hours>\d+)h){0,1}(?:(?P<minutes>\d+)m){0,1}(?:(?P<seconds>\d+)s){0,1}', str(s)).groupdict(0)

        return datetime.timedelta(**dict(((key, int(value))
                                  for key, value in d.items() )))


class Driver(APIView):
    def __init__(self):
        self.driver = can.CANDriver()

    def get(self, request):
        dr_status = self.driver.run()
        if dr_status:
            return Response("CAN Driver has started successfully")
        else:
            return Response("CAN USB unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        packet = json.loads(request.body)
        node = packet['node']
        channel = packet['channel']
        data = packet['data']
        if all([node, channel, data]):
            self.driver.send(node, channel, data)
            return Response("Packet sent")
        else:
            return Response("Bad Data", status=status.HTTP_400_BAD_REQUEST)









