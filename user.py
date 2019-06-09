#Erik Jastad CS494
#IRC user class

#this class is used to hold information for connected clients in the host IRC
class user():
	def __init__(self):
		self.name = None		#client name
		self.conn = None		#clients connection socket
		self.addr = None		#clients address
		self.room = []			#clients rooms
