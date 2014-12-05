import sqlite3 as lite
import sys
import threading

#Make these 

#import channels
#import nodes

class CANDataLogger:
	#Connect to Scanalysis Database
	def __init__(self):
		self.update_count = 0
		con = lite.connect('test_SCDB.db')
		cur = con.cursor()
		with con:
			cur.execute("DROP TABLE IF EXISTS PACKETS_DATA")
			#add whatever items we want to keep track of
			cur.execute("""CREATE TABLE PACKETS_DATA
						(Id INT PRIMARY KEY, speed REAL)""")
		
		
	#Returns most recent packet in database with requested node and channel	
	def poll(self, con, qnode, qchannel):
		cur = con.cursor()
		try:
			cur.execute("""SELECT MAX(TIME), DATA FROM PACKETS_RAW
						WHERE NODE = ? AND CHANNEL = ?""", (qnode, qchannel))
			return cur.fetchone()[1]
			
		except lite.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
			
		finally:
			cur.close()
		
	def update(self, con, speed):
		self.update_count += 1
		cur = con.cursor()
		try:
			#print('insertingsu')
			cur.execute("INSERT INTO PACKETS_DATA VALUES(?, ?)", (self.update_count, speed))

		except lite.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
			
		finally:
			cur.close()
			
			
			
class updateDB(threading.Thread):
	def __init__(self, event):
		threading.Thread.__init__(self)
		self.stopped = event
		self.data_log = CANDataLogger()
	
	def run(self):
		con = lite.connect('test_SCDB.db')
		with con:
			while not self.stopped.wait(5):
				print('Running thread \n')
				speed = self.data_log.poll(con, 1, 1)
				#Do this for all wanted values
				#print('Data value is %f' %speed)
				#Update entries in database
				self.data_log.update(con, speed)
			
			
		
		
			
		
		
		
		
		
	
			
			  
		
		
