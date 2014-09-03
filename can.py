__author__ = "varvara"

#from .packet import Packet

import threading
import time
import serial
from queue import Queue

BAUD = 115200
RX_BUF_LEN = 216

PKT_DELIM = "UNSW"
PKT_DELIM_LEN = 4

PKT_LEN = 18

class CANDriver:
    def __init__(self, port):
        # Database for logging received packets
        self.__packets_db = None 
        
        # Queue for packets read from serial
        self.__packets_read = Queue()
        #self.__packets_to_send = Queue()
        
        # Serial setup
        self.__port = port      # Port name e.g.: /dev/ttyUSB0
        self.__serial = None    # Serial instance

        # State indicators
        self.__running = False
        self.active = False

        # Threads
        self.__read_thread = threading.Thread(target=self.read)
        self.__read_thread.daemon = True

        #self.__send_thread = None
        
        self.__log_thread = None


        # Start driver
        self.run()

    def run(self):
        self.__running = True
        
        # Connect to serial port
        self.connect()
        
        # Start reading packets
        self.__read_thread.start()

    def connect(self):
        while self.__running:
            # Attempt to connect to serial port
            try:
                self.__serial = serial.Serial(self.__port, BAUD)
                self.__serial.write(b'rrr') # For CANUSB: enter raw mode
                self.active = True
                break
            except:
                print("Could not open serial port %s, retrying" % self.__port)
                self.active = False
                time.sleep(1)

    def stop(self):
        self.__running = False

    def read(self):
        packet     = []     # Store exact copy of packet (including delimiter)
        datastream = []     # Store datastream read from serial port
        
        packet_mode = False    # Flag for beggining to store packet when delimiter received

        current_char_index = 0 # Index of last char read from serialdata

        while self.__running:
            datastream = self.__serial.read(RX_BUF_LEN)
            
            # Read each serial data char
            current_char_index = -1
            for c in datastream:
                current_char_index += 1
                print(c)

                # Until full packet is received
                if len(packet) < PKT_LEN:
                    # Check if delimiter received
                    delim = datastream[current_char_index-PKT_DELIM_LEN:current_char_index+1]
                    if delim == PKT_DELIM:
                        # If we received new packet before previous finished - drop previous
                        if len(packet) > 0:
                            print("Dropped packet")
                        # Enter packet mode
                        packet = PKT_DELIM
                        packet_mode = True
                
                    # If delimiter received, start capturing packet
                    if packet_mode:
                        packet.append(c)
                
                # Recorded full packet, queue full packet
                if len(packet) >= PKT_LEN:
                    # TODO checksum stuff
                    # Calculate ID
                    pkt_id = 0
                    for i in range(RX_ID_LSB_INDEX, RX_ID_MSB_INDEX+1):
                        pkt_id = pkt_id | ord(packet[i]) << 8*(RX_ID_MSB_INDEX-i)

                    # Calculate data
                    data = []
                    length = ord(packet[RX_LEN_INDEX])
                    data_as_str = packet[RX_DATA_LSB_INDEX:RX_DATA_MSB_INDEX+1]
                    for data_char in data_as_str:
                        data.append(ord(data_char))

                    # Queue to be written to sqlite DB
                    self.__packets_read.put(Packet(pkt_id, data))

    def send(self):
        pass
