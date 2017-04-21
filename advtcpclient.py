# TCP connection test

import socket

TCP_IP = "127.0.0.1"
TCP_PORT = 9900
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

sendmessage = True

while sendmessage:
	MESSAGE = input('Message:')
	if MESSAGE != '00':
		s.send(MESSAGE.encode())
	else:
		sendmessage = False

	data = s.recv(BUFFER_SIZE)
	print("Id of the exo:", data.decode().split(":")[1])
s.close()

#TODO: Get back id of exo