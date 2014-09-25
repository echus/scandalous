__author__ = "varvara"

#from .packet import Packet

import threading
import time
import serial
from queue import Queue

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

class Packet:
    """Object for storing CAN packet"""
    def __init__(self, id, data):
        self.id   = id
        self.data = data

    def __str__(self):
        return ''.join(["ID: ", str(self.id), " Data: ", str(self.data)])
    #def __init__(self, address, channel, time, data):
    #    self.address = address
    #    self.channel = channel
    #    self.time = time
    #    self.data = data

class CANDriver:
    def __init__(self, port=PORT_DEFAULT):
        # Database for logging received packets
        self.__packets_db = None 
        
        # Serial setup
        self.__port = port      # Port name e.g.: /dev/ttyUSB0
        self.__serial = None    # Serial instance

        # State indicators
        self.__running = False
        self.active = False

        # Threads
        self.__read_thread = None
        #self.__send_thread = None
        self.__write_thread = None

        # Start driver
        #self.run()

    def run(self):
        print("CANDriver run() called")
        
        # Connect to serial port
        ser = self.connect()
        print("Connected to serial port")
        
        # Start reading packets
        self.__read_thread = CANReadThread(ser)
        self.__read_thread.start()

        # TESTING - print all packets in queue while thread is running
        #while True:
        #    pkt = self.__read_thread.packets.get()
        #    print("Got packet", pkt)
        #    self.__read_thread.packets.task_done()

    def connect(self):
        """Attempt to connect to Driver's specified serial port"""
        while True:
            # Attempt to connect to serial port
            try:
                ser = serial.Serial(self.__port, BAUD)
                ser.write(b'rrr') # For CANUSB: enter raw mode
                return ser
            except:
                print("Could not open serial port %s, retrying" % self.__port)
                self.active = False
                time.sleep(1)

    def stop(self):
        """Stop execution"""
        self.__running = False

    def send(self):
        """Process queued packets and write to sqlite"""
        #self.__packets_to_write

    def log(self):
        pass

class CANReadThread(threading.Thread):
    """Read CAN packets from specified serial port"""
    def __init__(self, ser):
        super(CANReadThread, self).__init__()
        self.__ser   = ser     # Serial port to read from (Serial obj)
        self.packets = Queue() # Queue for packets read from serial
        self.stop    = False   # Stop flag

    def run(self):
        packet     = []     # Store exact copy of packet (including delimiter)
        datastream = []     # Store datastream read from serial port
        
        packet_mode = False    # Flag for beggining to store packet when delimiter received

        print("Reading packets!")
    
        while not self.stop:
            #print("Looping")
            datastream = self.__ser.read(RX_BUF_LEN)
            
            #print("Read datastream")
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
                        packet = list(PKT_DELIM) # Record delimiter at start of packet
                        packet_mode = True
                
                    # If delimiter received, start capturing packet
                    if packet_mode:
                        #print("In packet mode, capturing packet, current length:", len(packet))
                        packet.append(char)
                
                # Recorded full packet, queue full packet
                if len(packet) >= PKT_LEN:
                    #print("Packet received, I think")
                    # TODO checksum stuff
                    # Calculate ID
                    pkt_id   = self.calc_packet_id(packet)
                    pkt_data = self.calc_packet_data(packet)
                    pkt = Packet(pkt_id, pkt_data)

                    print("Packet received", pkt)

                    # Queue packet
                    self.packets.put(Packet(pkt_id, pkt_data))

                    # TESTING stop after 100 packets to check running
                    qsize = self.packets.qsize()
                    print("Packets queued", qsize)
                    if qsize > 100:
                        self.stop = True

    @staticmethod
    def calc_packet_id(packet):
        pkt_id = 0
        for i in range(RX_ID_LSB_INDEX, RX_ID_MSB_INDEX+1):
            pkt_id = pkt_id | packet[i] << 8*(RX_ID_MSB_INDEX-i)
        return pkt_id

    @staticmethod
    def calc_packet_data(packet):
        data = []
        length = packet[RX_LEN_INDEX]
        data_as_str = packet[RX_DATA_LSB_INDEX:RX_DATA_MSB_INDEX+1]
        for data_char in data_as_str:
            data.append(data_char)
        return data



class CANWriteThread(threading.Thread):
    def __init__(self):
        super(CANWriteThread, self).__init__()

    def run(self):
        while True:
            print("Writing")

# For testing
if __name__ == "__main__":
    driver = CANDriver()
    driver.run()
