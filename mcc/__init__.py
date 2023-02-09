
from .data import Buffer, Packet, to_buffer, from_buffer
from .tables import *

from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout
from colorama import just_fix_windows_console
from threading import Thread
from time import sleep, time
from queue import Queue

import struct
import zlib
import json
import yaml
import os

just_fix_windows_console()

def PACK(buffer, num=None):
	buffer.seek(0)
	VarInt.write(len(buffer.bytes) if num is None else num, buffer)

def UNPACK(buffer):
	return VarInt.read(buffer)

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

class Main:
	version = {
		'1.18.2': 758
	}

	data = {}
	threshold = 256
	active = True

	def __init__(self):
		self.queue = Queue()
		self.color = False
		self.listen_chat = None

	def send_raw(self, packid, buffer, state='play'):
		PACK(buffer)
		buffer.seek(0)
		VarInt.write(packid, buffer)
		if state == 'play' and self.threshold >= 0:
			PACK(buffer, 0)
		PACK(buffer)
		self.socket.send(buffer.bytes)

	def send(self, _id, *args, state='play'):
		if type(_id) == Packet:
			self.send_raw(packet.id, packet.to_buffer(state=state), state=state)
		else:
			self.send_raw(_id, to_buffer(_id, list(args), state=state), state=state)

	def read_uncompressed(self, buffer):
		length = VarInt.read(buffer)
		id = VarInt.read(buffer)
		return length, id

	def read(self, buffer, state='play'):
		res = []
		res.append(VarInt.read(buffer))                           # 0 Размер пакета
		res.append(VarInt.read(buffer) if state == 'play' else 0) # 1 Размер данных

		if res[1] > 0:
			data = zlib.decompress(buffer.read())
			buffer = Buffer(data)
			buffer.seek(0)

		res.append(VarInt.read(buffer))                           # 2 ID пакета
		res.append(from_buffer(res[2], buffer, state=state))      # 3 Список с данными
		res.pop(1)
		return res

	def reconnect(self, addr):
		self.socket.close()

		self.socket = Socket(AF_INET, SOCK_STREAM)
		self.socket.settimeout(1)

		self.socket.connect(addr)

	def connect(self, addr=('localhost', 25565), username='PythonBot'):
		self.addr = addr
		self.data['host'] = addr[0]
		self.data['port'] = addr[1]
		self.data['username'] = username

		self.socket = Socket(AF_INET, SOCK_STREAM)
		self.socket.settimeout(1)
		try:
			self.socket.connect(addr)
		except ConnectionRefusedError:
			raise SystemExit('Сервер не доступен')

		# отправляем запрос о статусе
		self.send(0x00, self.version['1.18.2'], addr[0], addr[1], 1, state='login')
		self.send(0x00, state='tostatus')

		# получаем данные содержащие статус
		buffer = self.recv_raw()
		size, _id, data = self.read(buffer, state='status') # получаем 0x00 пакет
		if _id == 0x1A:
			print(yaml.dump(data[0]))
			exit()

		self.reconnect(addr)

		# Handshake
		# отправляем запрос на подключение
		self.send(0x00, self.version['1.18.2'], addr[0], addr[1], 2, state='login')
		self.send(0x00, username, state='tologin')
		
		buffer = self.recv_raw()
		size, _id, data = self.read(buffer, state='login') # получаем 0x03 пакет
		self.threshold = data[0]

		# https://wiki.vg/Protocol#Login_Success
		buffer = self.recv_raw()
		size, _id, data = self.read(buffer, state='login') # получаем 0x02 пакет
		player.UUID = data[0]

		print('Вход выполнен')

		Thread(target=self.recv,daemon=True).start()
		Thread(target=self.main,daemon=True).start()
		sleep(0.5)
		Thread(target=self.update,daemon=True).start()

	# https://wiki.vg/index.php?title=Protocol&oldid=17499
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Death_Combat_Event
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Respawn

	def recv_raw(self):
		try:
			# max 2097151 bytes
			data = self.socket.recv(1024**2*2)
		except ConnectionAbortedError:
			raise Exception('Соединение разорвано')

		if not data:
			raise Exception('Сервер перестал отвечать')

		buffer = Buffer(data)
		buffer.seek(0)
		return buffer

	def update(self):
		while self.active:
			self.send(0x14, 'Boolean True')
			sleep(1/20)

	def recv(self):
		while self.active:
			try:
				buffer = self.recv_raw()
			except timeout:
				pass
			except Exception as e:
				self.active = False
				raise e
			else:
				self.queue.put(buffer)

	def main(self):
		while self.active:
			try:
				buffer = self.queue.get()

				PacketLength = VarInt.read(buffer)
				DataLength = VarInt.read(buffer)

				if DataLength > 0:
					# continue
					data = zlib.decompress(buffer.read())
					buffer = Buffer(data)
					buffer.seek(0)

				PacketID = VarInt.read(buffer)
				if PacketID == 0x21:
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28clientbound.29
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28serverbound.29
					KeepAliveID = Long.read(buffer)
					self.send(0x0F, KeepAliveID)
					# print('keep Alive ID:', KeepAliveID)

				# elif PacketID == 0x00:
				# 	Player.EntityID = VarInt.read(buffer)
				# 	Player.UUID = UUID.read(buffer)
				# 	Player.Type = VarInt.read(buffer)
				# 	Player.X = Double.read(buffer)
				# 	Player.Y = Double.read(buffer)
				# 	Player.Z = Double.read(buffer)
				# 	Player.Pitch = 1 / UnsignedByte.read(buffer)
				# 	Player.Yaw = 1 / UnsignedByte.read(buffer)
				# 	Player.Data = Int.read(buffer)
				# 	Player.VelocityX = Short.read(buffer)
				# 	Player.VelocityY = Short.read(buffer)
				# 	Player.VelocityZ = Short.read(buffer)
				# 	print('0x00 данные получены!')

				# elif PacketID == 0x04:
				# 	Player.EntityID = VarInt.read(buffer)
				# 	Player.UUID = UUID.read(buffer)
				# 	Player.X = Double.read(buffer)
				# 	Player.Y = Double.read(buffer)
				# 	Player.Z = Double.read(buffer)

				# 	# print('XYZ', Player.X, Player.Y, Player.Z)

				# 	Player.Pitch = 1 / UnsignedByte.read(buffer)
				# 	Player.Yaw = 1 / UnsignedByte.read(buffer)
				# 	print('0x04 данные получены!')

				# elif PacketID == 0x0F:
				# 	data = Json.read(buffer)
				# 	_type = Byte.read(buffer)
				# 	sender = UUID.read(buffer)
				# 	# print(sender)
				# 	# print(yaml.dump(data))

				# 	if _type == 0:
				# 		name = data['with'][0]['text']
				# 		text = data['with'][1]
				# 		print(f'<{name}> {text}')

				# 	if _type == 1:
				# 		if 'with' in data:
				# 			try:
				# 				if data['with'][0]['text'] == 'Server':
				# 					text = data['with'][1]['text']
				# 					print(f'[Server] {text}')
				# 				else:
				# 					print(data['with'][0]['text'])
				# 			except:
				# 				print(yaml.dump(data))

				# 		elif 'extra' in data:
				# 			if 'color' in data and data['color'] in color_name:
				# 				print(color_name[data['color']], end='')

				# 			try:
				# 				for line in data['extra']:
				# 					color = ''
				# 					if 'color' in line and line['color'] in color_name:
				# 						color = color_name[line['color']]
									
				# 					text = ''
				# 					if 'text' in line:
				# 						text = line['text']

				# 					elif 'translate' in line:
				# 						name = data['extra'][0]['translate']
				# 						if name == 'command.unknown.command':
				# 							text = 'неизвестная команда'

				# 					print(color + text + Fore.RESET, end='')
				# 				print('')
				# 			except:
				# 				print(yaml.dump(data))
				# 		else:
				# 			print(yaml.dump(data))

				elif PacketID == 0x1A:
					data = Json.read(buffer)
					print(data['translate'])

				elif PacketID == 0x35 or PacketID == 0x3D:
					self.send(0x04, 0) # Respawn

				elif PacketID == 0x38:
					print('0x38 данные получены!')
					p = player
					p.x , p.y, p.z, p.yaw, p.pitch, p.flags, p.tpid = self.read(buffer, R'3%Double 2%Float Byte VarInt')
					# p.x , p.y, p.z, p.yaw, p.pitch, p.flags, p.tpid = from_buffer(0x38, buffer)

					self.send(0x00, p.tpid)

				elif PacketID == 0x52: # Update Health
					Health = Float.read(buffer)
					if Health == 0:
						self.send(0x04, 0) # Respawn

			# except (ValueError, timeout, struct.error):
			# 	continue

			except Exception as e:
				self.active = False
				raise e

			self.queue.task_done()