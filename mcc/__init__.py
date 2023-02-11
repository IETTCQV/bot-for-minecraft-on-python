
from .data import *
from .tables import *

from threading import Thread
from time import sleep, time
from queue import Queue

import zlib
import yaml

class player:
	EntityID = None
	UUID = None
	Type = None
	x = None
	y = None
	z = None
	pitch = None
	yaw = None
	Data = None
	VelocityX = None
	VelocityY = None
	VelocityZ = None


class Bot:
	# https://wiki.vg/index.php?title=Protocol&oldid=17499
	from .manage.data import send, recv, read
	from .manage.sock import close, connect
	from .manage.app import error

	threshold = 256
	running = True
	socket = None

	version = {
		'1.18.2': 758
	}

	def __init__(self):
		self.queue = Queue()

	def run(self, addr=('localhost', 25565), username='PythonBot'):
		self.addr = addr
		self.username = username
		self.connect()

		# Handshake
		# отправляем запрос на подключение
		self.send(0x00, self.version['1.18.2'], addr[0], addr[1], 2, state='handshake')
		self.send(0x00, username, state='login')
		
		# получаем 0x03 пакет
		buffer = Buffer(self.socket.recv(1024))
		_ = VarInt.read(buffer)
		id = VarInt.read(buffer)

		if id == 0x03:
			self.threshold = VarInt.read(buffer)
		else:
			print(hex(id), 'другой пакет (ожидался 0x03)')
			exit()

		# if id in [0x00, 0x1A]:
		# 	print(yaml.dump(data[0]))
		# 	exit()

		# получаем 0x02 пакет
		buffer = Buffer(self.socket.recv(1024))
		_ = VarInt.read(buffer)
		_ = VarInt.read(buffer)
		id = VarInt.read(buffer)

		if id == 0x02:
			player.UUID = UUID.read(buffer)
		else:
			print(hex(id), 'другой пакет (ожидался 0x02)')
			print(buffer.bytes)
			exit()

		print('Вход выполнен')

		Thread(target=self.recv,daemon=True).start()
		Thread(target=self.main,daemon=True).start()
		sleep(0.5)
		Thread(target=self.update,daemon=True).start()

	def update(self):
		while self.running:
			self.send(0x14, True)
			sleep(1)

	def main(self):
		while self.running:
			try:
				data = self.queue.get()
				id, data = self.read(data)

				# 0x26 join player
				# 0x18 Plugin Message
				# 0x0E Server Difficulty
				# 0x48 Held Item Change
				# 0x66 Declare Recipes

				if id == 0x21:
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28clientbound.29
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28serverbound.29
					self.send(0x0F, data[0])
					print('keep Alive ID:', data[0])

				elif id == 0x1A:
					print(data[0]['translate'])

				elif id in [0x35, 0x3D]:
					# 0x35 - экран смерти, ID себя (VarInt), ID моба (Int), сообщение (Json)
					# 0x3D - данные для возраждения
					self.send(0x04, 0) # пакет для возраждения

				elif id == 0x38:
					print('0x38 данные получены!')
					p = player
					p.x, p.y, p.z, p.yaw, p.pitch, p.flags, p.tpid = data

					self.send(0x00, p.tpid)

				elif id == 0x52: # Update Health
					if data[0] == 0:
						self.send(0x04, 0) # Respawn

			except ValueError as e:
				pass
				# print(e)

			except zlib.error as e:
				pass
				# print(e)

			except (ConnectionAbortedError, ConnectionResetError) as e:
				pass
				# print(e)

			except Exception as e:
				# raise e
				self.error(f'__init__:main: {e}')
				self.running = False

			self.queue.task_done()