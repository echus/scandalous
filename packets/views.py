__author__ = 'Anmol'

from django.core.management import call_command
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from packets.models import Packet
from packets.serializers import PacketSerializer
from packets import can
import os
import json
import datetime
import re
import time
import scandalous
import logging

logger = logging.getLogger("scandalous.debug")

# All url /packet? queries processed here
class AnalyseQuery(APIView):
    # Sets Response to prioritise rendering in JSON format
    renderer_classes = [JSONRenderer]
    reverse_flag = False

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

        dsf = request.GET.get('dsf')

        if dsf is not None:
            if int(dsf) > 0:
                currQS = self.downsample(int(dsf), currQS)
            else:
                return Response("Downsampling factor invalid")

        if self.reverse_flag is True:
            currQS = reversed(currQS)

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
        self.reverse_flag = True
        packetlist = currQS.order_by('pkt_id')[:num_offset]
        return packetlist

    # Return "limit" packets starting from "offset" packet. i.e. If limit = 10, offset = 100, return packets 90->100
    def filter_limit_offset(self, num_limit, num_offset, currQS):
        self.reverse_flag = True
        packetlist = currQS.order_by('pkt_id')[num_offset-num_limit:num_offset]
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

    #Downsample queryset
    def downsample(self, dsf, currQS):
        packetlist = currQS[::dsf]
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
    driver = can.CANDriver()
    switch = None

    def get(self, request):
        logging.debug(self.driver)

        if self.switch is 0:
            dr_status = self.driver.run()
            if dr_status is not None:
                return Response("CAN Driver has started successfully")
            else:
                return Response("CAN USB unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        elif self.switch is 1:
            run_status = self.driver.stop()

            if run_status is 1:
                self.backup()
                return Response("CAN Driver has stopped successfully, packet table backed up")
            elif run_status is 0:
                return Response("CAN Driver was not running")

        elif self.switch is 2:
            self.backup()
            return Response("Packet table backed up")

        elif self.switch is 3:
            Packet.objects.all().delete()
            return Response("Packet table flushed")

        else:
            return Response("Something went wrong")

    def post(self, request):
        packet = json.loads(request.body.decode('utf-8'))
        node = packet['node']
        channel = packet['channel']
        data = packet['data']
        msg_type = packet['msg_type']
        timestamp = int(time.time() * 1000)
        if all([node, channel, msg_type, data, timestamp]):
            pkt_status = self.driver.send(node, channel, msg_type, data, timestamp)
            if pkt_status is not None:
                return Response("Packet sent")
            else:
                return Response("Failed to send packet")
        else:
            return Response("Bad Data", status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def backup():
        output_filename = datetime.datetime.now().strftime("%I:%M%p - %B %d %Y") + '.json'
        project_root = os.path.dirname(scandalous.__file__)
        output_path = os.path.join(project_root, 'backups/', output_filename)
        output = open(output_path, 'w+')
        call_command('dumpdata', 'packets', format='json', indent=4, stdout=output)
        output.close()









