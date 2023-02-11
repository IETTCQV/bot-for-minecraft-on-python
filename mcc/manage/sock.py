from socket import socket as Socket, AF_INET, SOCK_STREAM

def close(self):
	if self.socket != None:
		try: self.socket.close()
		except: pass
		self.socket = None

def connect(self):
	self.close()
	self.socket = Socket(AF_INET, SOCK_STREAM)
	self.socket.settimeout(20)
	try:
		self.socket.connect(self.addr)
	except ConnectionRefusedError:
		self.error('manage.sock: Сервер не доступен')