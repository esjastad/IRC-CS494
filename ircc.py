#Erik Jastad CS494
#IRC client

import socket
import threading
import os
import signal


#listening method ran in a thread, receives data from host
def listen(s):
	while True:
		try:
			idata = s.recv(1024) 		#receive,interpret and print the data from the host
			if not idata:
				break
			print(idata.decode("utf-8"))
		except socket.error:			#host connection lost
			print("Host connection lost!")
			os.kill(os.getpid(), signal.SIGTERM)
			break
	print("Host connection lost!")
	os.kill(os.getpid(), signal.SIGTERM)

#help method called when client types /help and displays information about how to use the IRC
def help():
	print("\nHere is a list of commands:")
	for i in commands:
		print(i)
	
	print("\n/create,/join,/leave and /delete expect a valid room. /leave all will leave all rooms")
	print("\n/whisper expects a valid user followed by a message, /broadcast just expects a message.")
	print("\n/rooms expects a valid room (or list of rooms seperated by a comma only NO SPACE) followed by a message.")
	print("\n/roomlist,/userlist,and /myrooms can be used alone.")
	print("\n/userlist followed by a room name will list the users in that room")
	print("\nType quit to disconnect from IRC session.\n")
	
	print("\n\nExample: /create funroom")
	print("Example: /join funroom")
	print("Example: /whisper dave Hello")
	print("Example: /rooms general,funroom Hello Everyone!")
	print("Example: /userlist")
	print("Example: /userlist general")	
	print("Example: /leave funroom")
	print("\nYou can also simply type in a message and everyone in your current room/rooms will see your message!\n")

#main, connects to host then creates a listening thread for display incoming data/msgs
if __name__ == "__main__":
	HOST = '127.0.0.1'  # The server's hostname or IP address
	PORT = 65432        # The port used by the server
	control = 0
	sdata = 0			#initialize variable for sending data
	commands = ['/help','/create','/join','/leave','/roomlist','/userlist','/delete','/whisper','/broadcast','/rooms','/myrooms']	#list of client commands

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		while (control == 0):
			try:
				s.connect((HOST, PORT))						#try to connect to host
				control = 1
			except socket.error:							#connection failed
				print("\nHost could not be reached on the default port!\n")
				PORT = int(input("Enter a port(-1 to quit):"))
				if PORT == -1:
					os.kill(os.getpid(), signal.SIGTERM)
					
		x = threading.Thread(target=listen, args=(s,))	#start thread for listening/recieving data
		x.start()
	
		print("\n\nWelcome to the IRC\n")
		print("Commands to use:\n")
		print(commands)
		print("\nTyping a message without a command will send your message to users in your room/rooms")
	
		sdata = input("Enter your username:") 			#Capture user message
		s.sendall(str.encode(sdata))    				#send user message
	
		while True:
			sdata = input(":")							#Capture user message

			if (sdata == 'quit'):   					#If user wants to quit
				break
			elif (sdata == '/help'):	
				help()
			else:
				try:
					s.sendall(str.encode(sdata))    	#send user message to host
				except socket.error:					#handle host disconnect
					print("Host connection lost!")
					break
					
	os.kill(os.getpid(), signal.SIGTERM)				
				



		
