from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout

socket = Socket()
socket.settimeout(0.1)

try:
	socket.connect(('127.0.0.0', 2000))
except Exception as e:
	print(str(e) == 'timed out')