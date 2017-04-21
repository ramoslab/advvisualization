# TCP connection test

# ### Imports ### #
import socket

# ### Configuration ### #
TCP_IP = "127.0.0.1"
TCP_PORT = 9900
BUFFER_SIZE = 1024

# ### Begin ### #

# Startup TCP interface
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# Send and receive messages
sendmessage = True
exit_message = ('q','quit','exit')

while sendmessage:
	MESSAGE = input('Send:')
	if MESSAGE not in exit_message:
		s.send(MESSAGE.encode())
	else:
		sendmessage = False

	data = s.recv(BUFFER_SIZE)
	print("Received:", data.decode().split(":")[1])

# Close connection
s.close()