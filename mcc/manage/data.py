from ..data import Buffer, to_buffer, from_buffer
from ..tables import dataformat
from ..types import VarInt
from socket import timeout

import zlib


def send(self, id, *args, state='play'):
	buffer = to_buffer(id, list(args), state=state)
	buffer.pack(VarInt, id)

	if state == 'play':
		if self.threshold >= 0 and len(buffer) >= self.threshold:
			self.error('manage.data: способ сжатия ещё не написан')
		else:
			buffer.pack(VarInt, 0)
	buffer.pack(VarInt, len(buffer))

	self.socket.send(buffer.bytes)

size = 1024**3*2
def recv(self):
	while self.running:
		# max 2097151 bytes
		try:
			data = self.socket.recv(size)

		except timeout:
			self.error('manage.data: Сервер перестал отвечать')
			break

		except:
			raise

		if len(data) == 0:
			self.error('manage.data: Сервер перестал отвечать')
			break

		self.queue.put(data)

def read(self, data):
	buffer = Buffer(data)
	buffer.seek(0)

	packet_length = VarInt.read(buffer)
	data_lenght = VarInt.read(buffer)

	if data_lenght > 0:
		data = zlib.decompress(buffer.read(data_lenght))
		buffer.clear()
		buffer.write(data)
		buffer.seek(0)

	id = VarInt.read(buffer)
	if id > 0x67:
		self.error(f'manage.data: ID пакета не существует ({hex(id)})')
		return [None, []]

	# Размер пакета, ID пакета, Список с данными
	if id in dataformat['recv']:
		return [id, from_buffer(id, buffer)]
	else:
		return [None, []]