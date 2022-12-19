
from .buffer import PacketBuffer
from .tables import *

from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout
from colorama import just_fix_windows_console
from threading import Thread
from time import sleep, time

import struct
import zlib
import json
import yaml
import os

just_fix_windows_console()

def PACK(buffer, num=None):
	data = buffer.bytes
	buffer.clear()
	VarInt.write(num if num != None else len(data), buffer)
	buffer.write(data)

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
	State = 'login'
	Threshold = 256
	buffer = []
	active = True

	def __init__(self):
		self.color = False
		self.listen_chat = None

	def send_raw(self, packid, *args):
		buffer = PacketBuffer()
		for func, value in args:
			func.write(value, buffer)

		PACK(buffer)
		buffer.seek(0)
		VarInt.write(packid, buffer)
		if self.State == 'play' and self.Threshold >= 0:
			PACK(buffer, 0)
		PACK(buffer)
		self.socket.send(buffer.bytes)

	def send(self, packid, text, *args):
		text = text.replace('\t', '')
		args = list(args)
		if ';' in text: p = ';'
		else: p = '\n'

		for line in text.split(p):
			if not line:
				continue

			name, value = line.split(' ', 1)
			name.replace(' ', '')
			if value[0] == '%':
				value = self.data[value[1:]]

			func = func_name[name]
			_type = func_type[name]
			value = _type(value)

			args.append((func, value))
		self.send_raw(packid, *args)

	def read_uncompressed(self, buffer):
		length = VarInt.read(buffer)
		id = VarInt.read(buffer)
		return length, id

	def read(self, buffer, text):
		res = []
		for name in text.split(' '):
			count = 1
			if '%' in name:
				count, name = name.split('%')
				count = int(count)

			if name not in func_name:
				continue

			func = func_name[name]

			for _ in range(count):
				res.append(func.read(buffer))
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
		self.send(0x00, R'''
			VarInt 0
			String %host
			UnsignedShort %port
			VarInt 1
		''')
		self.send_raw(0x00)

		# получаем данные содержащие статус
		buffer = self.recv_raw()
		
		length, id = self.read_uncompressed(buffer)
		data = Json.read(buffer)
		print(yaml.dump(data))

		self.reconnect(addr)

		# Handshake
		# отправляем запрос на подключение
		self.send(0x00, R'''
			VarInt 758
			String %host
			UnsignedShort %port
			VarInt 2
		''')
		self.send(0x00, R'String %username')
		
		buffer = self.recv_raw()
		PacketLength, PacketID = self.read_uncompressed(buffer)
		self.Threshold = VarInt.read(buffer)

		# https://wiki.vg/Protocol#Login_Success
		buffer = self.recv_raw()
		# print(buffer.bytes)
		PacketLength, PacketID = self.read_uncompressed(buffer)
		player.UUID = UUID.read(buffer)

		print('Вход выполнен')
		self.State = 'play'

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

		buffer = PacketBuffer(data)
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
				self.buffer.append(buffer)
				# print(len(self.buffer))

	def main(self):
		while self.active:
			try:
				while len(self.buffer) < 1:
					sleep(1 / 100)
				
				buffer = self.buffer.pop(0)

				PacketLength = VarInt.read(buffer)
				DataLength = VarInt.read(buffer)

				if DataLength > 0:
					# continue
					data = zlib.decompress(buffer.read())
					buffer = PacketBuffer(data)
					buffer.seek(0)

				PacketID = VarInt.read(buffer)
				if PacketID == 0x21:
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28clientbound.29
					# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28serverbound.29
					KeepAliveID = Long.read(buffer)
					self.send_raw(0x0F, (Long, KeepAliveID))
					# print('keep Alive ID:', KeepAliveID)

					'''
				elif PacketID == 0x00:
					Player.EntityID = VarInt.read(buffer)
					Player.UUID = UUID.read(buffer)
					Player.Type = VarInt.read(buffer)
					Player.X = Double.read(buffer)
					Player.Y = Double.read(buffer)
					Player.Z = Double.read(buffer)
					Player.Pitch = 1 / UnsignedByte.read(buffer)
					Player.Yaw = 1 / UnsignedByte.read(buffer)
					Player.Data = Int.read(buffer)
					Player.VelocityX = Short.read(buffer)
					Player.VelocityY = Short.read(buffer)
					Player.VelocityZ = Short.read(buffer)
					print('0x00 данные получены!')

				elif PacketID == 0x04:
					Player.EntityID = VarInt.read(buffer)
					Player.UUID = UUID.read(buffer)
					Player.X = Double.read(buffer)
					Player.Y = Double.read(buffer)
					Player.Z = Double.read(buffer)

					# print('XYZ', Player.X, Player.Y, Player.Z)

					Player.Pitch = 1 / UnsignedByte.read(buffer)
					Player.Yaw = 1 / UnsignedByte.read(buffer)
					print('0x04 данные получены!')
				'''

				elif PacketID == 0x0F:
					data = Json.read(buffer)
					_type = Byte.read(buffer)
					sender = UUID.read(buffer)
					# print(sender)
					# print(yaml.dump(data))

					if _type == 0:
						name = data['with'][0]['text']
						text = data['with'][1]
						print(f'<{name}> {text}')

					if _type == 1:
						if 'with' in data:
							try:
								if data['with'][0]['text'] == 'Server':
									text = data['with'][1]['text']
									print(f'[Server] {text}')
								else:
									print(data['with'][0]['text'])
							except:
								print(yaml.dump(data))

						elif 'extra' in data:
							if 'color' in data and data['color'] in color_name:
								print(color_name[data['color']], end='')

							try:
								for line in data['extra']:
									color = ''
									if 'color' in line and line['color'] in color_name:
										color = color_name[line['color']]
									
									text = ''
									if 'text' in line:
										text = line['text']

									elif 'translate' in line:
										name = data['extra'][0]['translate']
										if name == 'command.unknown.command':
											text = 'неизвестная команда'

									print(color + text + Fore.RESET, end='')
								print('')
							except:
								print(yaml.dump(data))
						else:
							print(yaml.dump(data))

				elif PacketID == 0x1A:
					data = Json.read(buffer)
					print(data['translate'])

				elif PacketID == 0x35 or PacketID == 0x3D:
					self.send_raw(0x04, (VarInt, 0)) # Respawn

				elif PacketID == 0x38:
					print('0x38 данные получены!')
					p = player
					p.x , p.y, p.z, p.yaw, p.pitch, p.flags, p.tpid = self.read(buffer, R'3%Double 2%Float Byte VarInt')

					self.send(0x00, f'VarInt {p.tpid}')

				elif PacketID == 0x52: # Update Health
					Health = Float.read(buffer)
					if Health == 0:
						self.send_raw(0x04, (VarInt, 0)) # Respawn

			# except (ValueError, timeout, struct.error):
			# 	continue

			except Exception as e:
				self.active = False
				raise e