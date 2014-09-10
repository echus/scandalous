import sqlite3 as lite
import sys
import threading

#Make these 
#import channels
#import nodes

class CANDataLog:
	def __init__(self):
        #Connect to Scanalysis Database
		con = lite.connect('Scanalysis.db')
        #Initialise clean packet data table
		cur = con.cursor()
		with cur:
			cur.execute("DROP TABLE IF EXISTS PACKETS_DATA")
			#add whatever items we want to keep track of
			cur.execute("""CREATE TABLE PACKETS_DATA
						(Id INT PRIMARY KEY, speed REAL""")
		
		
	#Returns most recent packet in database with requested node and channel	
	def poll(self, qnode, qchannel):
		try:
			cur = self.con.cursor()
			cur.execute("""SELECT MAX(TIME), DATA FROM PACKETS_RAW
						WHERE NODE = ? AND CHANNEL = ?""", (qnode, qchannel)
			return cur.fetchone()
			
		except lite.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
			
		finally:
			cur.close()
		
    #Update packet data table
	def update(self, speed):
		try:
			cur = self.con.cursor()
			packet = self.poll(qnode, qchannel)
			#perform any scaling needs here
			cur.execute("INSERT INTO PACKETS_RAW VALUES(?,)", speed)

		except lite.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
			
		finally:
			cur.close()
			
			
#Updates packet data table every 5 seconds when thread started
class updateDB(threading.Thread):
	def __init__(self, event, name):
		threading.Thread.__init__(self)
		self.stopped = event
		data_log = CANDataLog()
	
	def run(self):
		while not self.stopped.wait(5):
			speed = self.data_log.poll(SPEEDNODE, SPEEDCHANNEL)
			#Do this for all wanted values
			
			#Update entries in database
			self.data_log.update(speed)