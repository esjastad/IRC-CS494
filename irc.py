#Erik Jastad CS494
#IRC host

import threading
import socket
import user
import signal
import os



#globals being used
clients = []
rooms = []
rooms.append('general')	#default user room

#this method sends the data/msg to all clients except the sending user
def broadcast(data, uname):
	for i in clients:
		if (i.name == uname):
			continue
		i.conn.sendall(data)

#this method sends data/msg to rooms matching the list of rooms in the input room
def roomcast(data, room, uname): 
	if (isinstance(room, list)):							#check if the room is a list
		if (len(room) > 1):									#check if there is more than 1 room
			for i in room:
				for j in clients:
					if (i in j.room and j.name != uname):	#if the client is in the room and not the sender, send the message
						whisper(str.encode("(" + i + data),j)
		else:
			for i in clients:								#for 1 room list
				if (room[0] in i.room and i.name != uname):
					whisper(str.encode("(" + room[0] + data),i)
	else:						
		for i in clients:									#for a room that was not a list of rooms
			if (room in i.room and i.name != uname):
				whisper(str.encode("(" + room + data),i)

#this method sends a msg to the passed in client as person
def whisper(data,person):
	person.conn.sendall(data)

#this method removes the culler string from the cullee string	
def cull(cullee, culler):
	cullee = cullee.split(culler)
	try:							#if theres is a [1] index
		return cullee[1]
	except:
		return cullee[0]

#this method checks the client message for commands begining with a / and executes the valid command		
def analyze(data, nuser):
	if (data[0] == '/'):							#check if the string starts with /
		temp = data.split(' ')						#split the string at a space
		if (temp[0] == "/create"):
			name = cull(data,"/create ")
			
			if (name.isspace() or name == ''):		#check if the room to be created has a valid name not just spaces
				nuser.conn.sendall(str.encode("No valid room name was given! type /help for proper use of /create"))
			elif (name[0] == '/'):					#check if the room is being made with a / at the start
				nuser.conn.sendall(str.encode("No valid room name was given! type /help for proper use of /create"))
				
			else:
				if name in rooms:					#Check if the room already exists
					nuser.conn.sendall(str.encode("The room you are trying to create already exists!"))
				else:								#make the room if all checks passed
					rooms.append(name)
					nuser.conn.sendall(str.encode(name + " room was created!"))

		elif (temp[0] == "/join"):
			name = cull(data,"/join ")
			if (name in rooms):
				if (name in nuser.room):			#check if the user is already in the room theyre attempting to join
					nuser.conn.sendall(str.encode("You are already in this room!"))
				else:								#join the room if it exists
					nuser.room.append(name)
					roomcast((" chat) Message: " + nuser.name + " has joined the room!"),name, 'Server')
			else:
				nuser.conn.sendall(str.encode("The room you were trying to join was not found!"))
						
		elif (temp[0] == "/roomlist"):				#list the servers rooms
			nuser.conn.sendall(str.encode("IRC Room List:\n"))
			for i in rooms:
				nuser.conn.sendall(str.encode(i+"\n"))
		
		elif (temp[0] == "/userlist"):				#list the users on the server
			name = cull(data,"/userlist ")
			if (name.isspace() or name == ''):
				nuser.conn.sendall(str.encode("IRC User List:\n"))			
				for i in clients:
					nuser.conn.sendall(str.encode(i.name+"\n"))
			elif (name[0] == '/'):
				nuser.conn.sendall(str.encode("IRC User List:\n"))			
				for i in clients:
					nuser.conn.sendall(str.encode(i.name+"\n"))
			else:									#list the user in a specified room
				if name in rooms:
					nuser.conn.sendall(str.encode(name + " room user list:\n"))
					for i in clients:
						if name in i.room:
							nuser.conn.sendall(str.encode(i.name + "\n"))
				else:
					nuser.conn.sendall(str.encode("The room you were trying to list users for was not found!"))
					
				
		elif (temp[0] == "/leave"):					#leave a specified room or all rooms
			name = cull(data,"/leave ")
			if (name == 'all'):
				for i in nuser.room:
					roomcast((" chat) Message: " + nuser.name + " has left the room!\n"),i, 'Server')
				nuser.room = []
				
			elif (name in nuser.room):
				roomcast((" chat) Message: " + nuser.name + " has left the room!"),name, 'Server')
				nuser.room.remove(name)
			else:
				nuser.conn.sendall(str.encode("You are not currently in that room, or no room was specified!"))

		elif (temp[0] == "/delete"):				#delete a specified room
			name = cull(data,"/delete ")
			safe = 1
			if (name == 'general'):					#cant delete the general room
				nuser.conn.sendall(str.encode("The general room can not be deleted!"))
			elif (name in rooms):
				for i in clients:					#check if clients are in the room to delete
					if (name in i.room):
						safe = 0
						break
				
				if (safe == 1):						#if no clients in room then delete it
					rooms.remove(name)
					nuser.conn.sendall(str.encode(name + " room was deleted!"))
				else:
					nuser.conn.sendall(str.encode(name + " room has active users and could not be deleted!"))
			else:									#room to delete not found
				nuser.conn.sendall(str.encode(name + " room was not found!"))
	
		elif (temp[0] == "/broadcast"):				#broadcast message to all users
			data = cull(data,"/broadcast ")
			data = "(Broadcast chat) " + nuser.name + ": " + data
			broadcast(str.encode(data),nuser.name)
			
		elif (temp[0] == "/whisper"):				#whisper to a specified user
			data = cull(data,"/whisper ")
			temp = data.split(' ')
			friend = None
			for i in clients:						#find the client to whisper
				if (i.name == temp[0]):
					friend = i
					break
			
			if (friend != None):					#whisper the client if found
				data = cull(data, (temp[0] + ' '))
				data = "(Whisper) " + nuser.name + ": " + data
				whisper(str.encode(data),friend)
			else:
				nuser.conn.sendall(str.encode(temp[0] + " was not found!"))

		elif (temp[0] == "/rooms"):					#message a room or list of rooms
			data = cull(data,"/rooms ")
			temp = data.split(' ')
			flag = 0
			
			if (len(temp) < 2):						#check for room/rooms followed by a message
				nuser.conn.sendall(str.encode("No rooms or message was not specified, please use /help for proper use of /rooms!"))
			else:
				msg = temp[1]			
				chan = temp[0].split(',')			#split the list of rooms seperated by comma
				size = len(chan)					#how many rooms to do
			
				for i in range (size):
					if chan[0] in rooms:			#if the room to message exists send the message
						ndata = (" chat) " + nuser.name + ": " + msg + "\n")
						roomcast(ndata,chan[0],nuser.name)
					else:							#if the room doesnt exist send a message to sender and continue processing
						flag = 1
						nuser.conn.sendall(str.encode(chan[0] + " room was not found!\n"))
					
					data = cull(temp[0], (chan[0] + ','))
					temp = data.split(' ')
					chan = temp[0].split(',')
				if flag == 0:						#inform the sender of their success or failure
					nuser.conn.sendall(str.encode("All rooms received your message!\n"))
				else:
					nuser.conn.sendall(str.encode("All other rooms received your message!\n"))

		elif (temp[0] == "/myrooms"):				#list the rooms the asking client is currently in
			nuser.conn.sendall(str.encode("Rooms you are currently in:\n"))
			for i in nuser.room:
				nuser.conn.sendall(str.encode(i + "\n"))
			
		else:										#/found but no valid command
			data = str.encode("Unrecognized command, type /help to see commands!")
			nuser.conn.sendall(data)
			
		return 0
	else:
		return 1

#this method listen for connecting users, it is ran in a thread from main
def listener(s):
	while True:
		try:
			s.listen()					#listen for socket connections
			conn, addr = s.accept()		#accept the connection, get a conn socket and grab the address
			nuser = user.user()			#create a user object
			nuser.conn = conn			#store the connection info
			nuser.addr = addr
			nuser.name = None
		
			rs = threading.Thread(target=rcvsnd, args=(nuser,))	#start a receiving thread for the connected user
			rs.start()
		except socket.error:			#when the socket failed or is disconnected break the loop
			break

#this method is for connected users, ran as a thead.  Receives client data calls the analyzer and takes action if necessary
def rcvsnd(nuser):
	if ('general' not in nuser.room):	#put the new user in the general room
		nuser.room.append(rooms[0])
	
	while (nuser.name == None):				#get a valid username
		data = nuser.conn.recv(1024)		#receive the user name
		nuser.name = data.decode("utf-8")
		
		if (nuser.name.isspace() or nuser.name == ''):		#check for valid name and/or duplicate name on server
			nuser.conn.sendall(str.encode("Please enter a valid user name!"))
			nuser.name = None
		elif (nuser.name[0] == '/'):
			nuser.conn.sendall(str.encode("Please enter a valid user name without a '/' character!"))
			nuser.name = None
		else:
			for i in clients:
				if i.name == nuser.name:
					nuser.conn.sendall(str.encode(nuser.name + " is already in use, please enter a different name!"))	
					nuser.name = None
	
	
	clients.append(nuser)					#user validated, add to client list
	
	data = str.encode("Server Message: " + nuser.name + " has joined the IRC session\n")	#send messages to other clients about the newly connected client
	broadcast(data, 'Server')
	data = " chat) Message: " + nuser.name + " has joined the room"
	roomcast(data, rooms[0], 'Server')
	
	with nuser.conn:
		try:
			while True:							#while connected
					data = nuser.conn.recv(1024)	#receive data
					if not data:
							break
					val = analyze(data.decode("utf-8"), nuser)	#analyze data
					if val == 1:					#if analyzer took no action,then send the data to all rooms the sending client is a part of
						data = " chat) " + nuser.name + ": " + data.decode("utf-8")
						if (len(nuser.room) >= 1):
							roomcast(data,nuser.room,nuser.name)
					
		except socket.error:			#When a client disconnects let other users know and break the loop
			for i in clients:
				if (i.name == nuser.name):
					clients.remove(i)
					data = str.encode(nuser.name + " has left the IRC session")
					broadcast(data,'Server')
					break
		for i in clients:
			if (i.name == nuser.name):
				clients.remove(i)
				data = str.encode(nuser.name + " has left the IRC session")
				broadcast(data,'Server')
				break
		
#main starts the socket connection and listening thread
if __name__ == "__main__":
	HOST = '127.0.0.1'
	PORT = 65432
	control = 0
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:		
		while (control == 0):
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			try:
				s.bind((HOST, PORT))	#bind the host and port into the socket
				control = 1
			except socket.error:
				print("\nDefault port is not available!\n")
				PORT = int(input("Enter a port(-1 to quit):"))
				if PORT == -1:
					os.kill(os.getpid(), signal.SIGTERM)

		l = threading.Thread(target=listener, args=(s,))	#start thread
		l.start()
		
		host = 'Go'
		while (host != 'quit'):								#until the host types quit
			host = input("Command:")
	os.kill(os.getpid(), signal.SIGTERM)					#kill the process and running threads


	
		

	
	

