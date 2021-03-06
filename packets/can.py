views__author__ = "varvara"

import sys
import threading
import serial
import logging
import time
import datetime
import struct
from packets.scandal_constants import ScandalConstants as SC
from queue import Queue
from packets.models import Packet

logger = logging.getLogger("scandalous.debug")

BAUD = 115200
RX_BUF_LEN = 216

PKT_DELIM = b'UNSW'
PKT_DELIM_LEN = 4

PKT_LEN = 18

RX_DEL_LSB_INDEX  = 0
RX_DEL_MSB_INDEX  = 3
RX_ID_LSB_INDEX   = 4
RX_ID_MSB_INDEX   = 7
RX_DATA_LSB_INDEX = 8
RX_DATA_MSB_INDEX = 15
RX_LEN_INDEX      = 16
RX_CHKSUM_INDEX   = 17

PORT_DEFAULT = "/dev/ttyUSB0"

class CANDriver:
    def __init__(self, port=PORT_DEFAULT):
        # Serial setup
        self.__port = port      # Port name e.g.: /dev/ttyUSB0
        self.__serial = None    # Serial instance

        #DEBUG logs
        #logging.basicConfig(filename='debug.log', level=logging.INFO)

        # State indicators
        self.__running = False
        self.active = False
        self.packets = Queue()

        # Threads
        self.__read_thread = None
        self.__write_thread = None


    def run(self):
        print("CANDriver run() called")

        # Connect to serial port
        ser = self.connect()
        if ser is not None:
            print("Connected to serial port")
            logger.debug("Connected to Serial port: %s /n", ser)
            self.__serial = ser
            self.__running = True

            # Start reading packets
            self.__read_thread = CANReadThread(ser, self.packets)
            self.__read_thread.daemon = True
            self.__read_thread.start()

            # Start writing packets
            self.__write_thread = CANWriteThread(self.packets)
            self.__write_thread.daemon = True
            self.__write_thread.start()
        return ser

    def connect(self):
        """Attempt to connect to Driver's specified serial port"""

        try:
            ser = serial.Serial(self.__port, BAUD)
            ser.write(b'rrr') # For CANUSB: enter raw mode
            return ser
        except:
            print("Could not open serial port ", self.__port)
            # logger.debug("Could not open serial port %s", self.__port)
            self.active = False
            time.sleep(1)
            return None

    def stop(self):
        """Stop execution"""
        if self.__running is False:
            return 0
        self.__running = False
        self.__read_thread.stop()
        self.__write_thread.stop()
        return 1

    def send(self, node, channel, msg_type, data, timestamp):
        logger.debug("Ser connection is: %s \n", self.__serial)
        if self.__running is False:
            return None

        # Calculate ID from relevant parameters
        id = (channel & 0x3FF) | \
                 ((node & 0xFF) << 10) | \
                 ((msg_type & 0xFF) << 18) | \
                 (0x3F << 26)

        # Store ID as list of bytes
        pkt_id = [(id >> 24) & 0xFF,
                  (id >> 16) & 0xFF,
                  (id >> 8) & 0xFF,
                  (id >> 0) & 0xFF]

        # Store data as list of bytes
        pkt_data = [(data >> 24) & 0xFF,
                    (data >> 16) & 0xFF,
                    (data >> 8) & 0xFF,
                    (data >> 0) & 0xFF,
                    (timestamp >> 24) & 0xFF,
                    (timestamp >> 16) & 0xFF,
                    (timestamp >> 8) & 0xFF,
                    (timestamp >> 0) & 0xFF]

        # VOODOO
        bytes = pkt_id + pkt_data
        bytes += list(range(0, (8-len(pkt_data)))) + [len(pkt_data)]

        checksum = 0
        for byte in bytes:
            checksum += byte
            if checksum > 255:
                checksum -= 256

        bytes += [checksum]

        send_pkt = struct.pack(b"B", ord(b"C"))

        for byte in bytes:
            if byte == ord('q') or \
                    byte == ord('r') or \
                    byte == ord('C') or \
                    byte == ord('\\'):
                send_pkt += b"\\"
            send_pkt += struct.pack(b"B", byte)

        send_pkt += b"r"
        logger.debug("Packet sent is: \n %s \n", send_pkt)
        # END VOODOO, send pkt through serial connection
        self.__serial.write(send_pkt)
        return 1

    def is_running(self):
        return self.__running

class CANReadThread(threading.Thread):
    """Read CAN packets from specified serial port"""
    def __init__(self, ser, packets):
        super(CANReadThread, self).__init__()
        self.__ser   = ser      # Serial port to read from (Serial obj)
        self.packets = packets  # Queue for packets read from serial
        self.stopped = threading.Event()    # Stop flag
        self.pkt_count = Packet.objects.all().count()      # Number of packets received
        # logger.debug("Have %i packets already", self.pkt_count)

    def run(self):
        packet     = []     # Store exact copy of packet (including delimiter)
        datastream = []     # Store datastream read from serial port

        packet_mode = False    # Flag for beginning to store packet when delimiter received

        print("Reading packets!")
        # logger.debug("Reading packets!")

        while not self.stopped.isSet():
            #print("Looping")
            #logger.debug("looping!")
            datastream = self.__ser.read(RX_BUF_LEN)

            #print("Read datastream")
            #logger.debug("Got datastream")
            # Read each serial data char
            testing = 0
            for charind, char in enumerate(datastream):
				

                #print(chr(char), end="")

                # Wait until full packet is received
                if len(packet) < PKT_LEN:
                    # Check if delimiter received
                    delim = datastream[charind-PKT_DELIM_LEN+1:charind+1]
                    #print("Potential delim", delim)

                    if delim == PKT_DELIM:
                        #print("Received delim:", delim)
                        # If we received new packet before previous finished - drop previous
                        if len(packet) > 0:
                            print("Dropped packet")
                        # Enter packet mode
                        packet = list(PKT_DELIM[:3])  # Record delimiter at start of packet
                        packet_mode = True

                    # If delimiter received, start capturing packet
                    if packet_mode:
                        #print("In packet mode, capturing packet, current length:", len(packet))
                        #print("Char is: ", char);
                        packet.append(char)

                # Recorded full packet, queue full packet
                if len(packet) >= PKT_LEN:
                    # logging.info('\nDEBUG PACKET IS: %s', packet)
                    #print("Packet received, I think")
                    # TODO checksum stuff
                    self.pkt_count += 1
                    # Calculate ID
                    pkt_id   = self.calc_packet_id(packet)
                    pkt_data = self.calc_packet_data(packet)
                    pkt_msg_type = self.calc_msg_type(pkt_id)
                    pkt_priority = self.calc_msg_priority(pkt_id)
                    pkt_timestamp = self.calc_packet_timestamp(pkt_data)
                    pkt_datetime = self.unix_time_to_date_time(pkt_timestamp)
                    pkt_node = self.calc_packet_node(pkt_id)
                    pkt_channel = self.calc_packet_ch(pkt_id)
                    pkt_val = self.calc_packet_val(pkt_data)

                    pkt = Packet(pkt_id=self.pkt_count, priority=pkt_priority, MSG_type=pkt_msg_type, time=pkt_datetime,
                                 node=pkt_node, channel=pkt_channel, data=pkt_val)
                    packet = []
                    packet_mode = False

                    #logging.info('Packet received %s', pkt)
                    # print("Debug ID: ", str(pkt_id), "\nDebug DATA: ", str(pkt_data), "\n\n")

                    # Queue packet
                    self.packets.put(pkt)
                    #print("Packets received: ", self.pkt_count)
                    #logger.debug("Packets received ", self.pkt_count)

    def stop(self):
        self.stopped.set()

    @staticmethod
    def calc_packet_id(packet):
        pkt_id = 0
        for i in range(RX_ID_LSB_INDEX, RX_ID_MSB_INDEX+1):
            pkt_id |= packet[i] << 8*(RX_ID_MSB_INDEX-i)
        return pkt_id

    @staticmethod
    def calc_packet_data(packet):
        data = []
        length = packet[RX_LEN_INDEX]
        data_as_str = packet[RX_DATA_LSB_INDEX:RX_DATA_MSB_INDEX+1]
        for data_char in data_as_str:
            data.append(data_char)
        return data

    @staticmethod
    def calc_packet_timestamp(data):
        scandal_timestamp = data[7] << 0 | \
            data[6] << 8 | \
            data[5] << 16 | \
            data[4] << 24
        return scandal_timestamp

    @staticmethod
    def calc_packet_node(ident):
        return ident >> SC.ADDR_OFFSET & 0xFF

    @staticmethod
    def calc_packet_ch(ident):
        return ident >> SC.SPECIFICS_OFFSET & 0x03FF

    @staticmethod
    def calc_packet_val(data):
        value = data[3] << 0 | \
            data[2] <<  8 | \
            data[1] << 16 | \
            data[0] << 24
        return value/1000

    @staticmethod
    def calc_msg_type(ident):
        return ident >> SC.TYPE_OFFSET & 0xFF

    @staticmethod
    def calc_msg_priority(ident):
        return ident >> SC.PRI_OFFSET & 0x07

    @staticmethod
    def unix_time_to_date_time(timestamp):
        dt = datetime.datetime.strptime(time.ctime(timestamp), "%a %b %d %H:%M:%S %Y")
        dt += datetime.timedelta(hours=15)
        return dt


# Thread - Stores queued Packet objects into django MYSQL database
class CANWriteThread(threading.Thread):
    def __init__(self, packets):
        super(CANWriteThread, self).__init__()
        self.stopped = threading.Event()
        self.packets = packets

    def run(self):
        while not self.stopped.isSet():
            #while True:
            #if self.packets.qsize() < 100:
            #     pass
            # else:
            #     break
            # print("Writing")
            pkt = self.packets.get()
            pkt.save()
            print("Packet Saved!")
            #logger.debug("Packet Saved!")

    def stop(self):
        self.stopped.set()
