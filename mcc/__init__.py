from . import types, colorama
from .types import *
from .buffer import PacketBuffer

from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread
from time import sleep, time
import struct

import zlib
import json
import yaml
import os

func_name = {
	'Boolean': Boolean,
	'UnsignedByte': UnsignedByte,
	'Byte': Byte,
	'Short': Short,
	'UnsignedShort': UnsignedShort,
	'Int': Int,
	'FixedPointInteger': FixedPointInteger,
	'VarInt': VarInt,
	'Long': Long,
	'UnsignedLong': UnsignedLong,
	'Float': Float,
	'Double': Double,
	'VarIntArray': VarIntArray,
	'ShortPrefixedByteArray': ShortPrefixedByteArray,
	'VarIntPrefixedByteArray': VarIntPrefixedByteArray,
	'TrailingByteArray': TrailingByteArray,
	'String': String,
	'Json': Json,
	'UUID': UUID
}

func_type = {
	'Boolean': bool,
	'UnsignedByte': int,
	'Byte': int,
	'Short': int,
	'UnsignedShort': int,
	'Int': int,
	'FixedPointInteger': int,
	'VarInt': int,
	'Long': int,
	'UnsignedLong': int,
	'Float': float,
	'Double': float,
	'VarIntArray': str,
	'ShortPrefixedByteArray': str,
	'VarIntPrefixedByteArray': str,
	'TrailingByteArray': str,
	'String': str,
	'Json': str,
	'UUID': str
}

def PACK(buffer, num=None):
	data = buffer.bytes
	buffer.clear()
	VarInt.write(num if num != None else len(data), buffer)
	buffer.write(data)

def UNPACK(buffer):
	return VarInt.read(buffer)

class Player:
	EntityID = None
	UUID = None
	Type = None
	X = None
	Y = None
	Z = None
	Pitch = None
	Yaw = None
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

			name, value = line.split(' ')
			name.replace(' ', '')
			if value[0] == '%':
				value = self.data[value[1:]]

			func = func_name[name]
			_type = func_type[name]
			value = _type(value)

			args.append((func, value))
		self.send_raw(packid, *args)

	def recv_raw(self):
		try:
			# max 2097151 bytes
			data = self.socket.recv(1024**2*2)
		except ConnectionAbortedError:
			raise Exception('Соединение разорвано')

		if not data:
			raise Exception('Сервер перестал отвечать')
			# data = b'\x00'

		buffer = PacketBuffer(data)
		buffer.seek(0)
		return buffer

	def read_uncompressed(self, buffer):
		length = VarInt.read(buffer)
		id = VarInt.read(buffer)
		return length, id

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

		'''
		# zlib.decompress
		# b'\xb3\x01\x00\xb0\x01{"description":{"text":""},"players":{"max":10,"online":1,"sample":[{"id":"09c06d59-947a-3bc5-9b2c-c1089c369248","name":"IvanExe"}]},"version":{"name":"1.18.2","protocol":758}}'
		# print(packet_length, data_length, buffer.read())
		'''

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
		Player.UUID = UUID.read(buffer)

		print('Вход выполнен')
		self.State = 'play'
		# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28clientbound.29
		# https://wiki.vg/index.php?title=Protocol&oldid=17499#Keep_Alive_.28serverbound.29

		# Thread(target=self.recv,daemon=True).start()
		Thread(target=self.main,daemon=True).start()
		# Thread(target=self.main,daemon=True).start()

	# https://wiki.vg/index.php?title=Protocol&oldid=17499
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Death_Combat_Event
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Respawn
	def recv(self):
		while self.active:
			try:
				buffer = self.recv_raw()
				self.buffer.append(buffer)

			except timeout:
				continue

			except Exception as e:
				self.active = False
				raise e

	def main(self):
		x = time()
		while self.active:
			# print('Буффер:', len(self.buffer))
			if time() - x >= 0.2:
				# x = time()
				self.send(0x14, 'Boolean True')

			try:
				# if len(self.buffer) == 0:
				# 	continue
				# buffer = self.buffer.pop(0)
				buffer = self.recv_raw()

				PacketLength = VarInt.read(buffer)
				DataLength = VarInt.read(buffer)

				if DataLength > 0:
					# print(PacketLength, 'СЖАТ')
					# continue
					data = zlib.decompress(buffer.read())
					buffer = PacketBuffer(data)
					buffer.seek(0)

				PacketID = VarInt.read(buffer)
				# print(PacketLength, DataLength, PacketID, buffer.bytes)
				if PacketID == 0x21:
					# 89 = Time Update
					# 41 = Entity Position
					# 33 = Keep Alive !!!

					KeepAliveID = Long.read(buffer)
					self.send_raw(0x0F, (Long, KeepAliveID))
					print('keep Alive ID:', KeepAliveID)

				elif PacketID == 0x00:
					'''
					0x00
					Entity ID		VarInt		Entity ID.
					Object UUID		UUID	
					Type			VarInt		The type of entity (same as in Spawn Living Entity).
					X				Double	
					Y				Double	
					Z				Double	
					Pitch			Angle		To get the real pitch, you must divide this by (256.0F / 360.0F)
					Yaw				Angle		To get the real yaw, you must divide this by (256.0F / 360.0F)
					Data			Int			Meaning dependent on the value of the Type field, see Object Data for details.
					Velocity X		Short		Same units as Entity Velocity. Always sent, but only used when Data is greater than 0 (except for some entities which always ignore it; see Object Data for details).
					Velocity Y		Short
					Velocity Z		Short
					'''

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
					'''
					0x04
					EntityID		VarInt		Player's EID.
					PlayerUUID		UUID		See below for notes on offline mode and NPCs.
					X				Double	
					Y				Double	
					Z				Double	
					Yaw				Angle	
					Pitch			Angle
					'''

					Player.EntityID = VarInt.read(buffer)
					Player.UUID = UUID.read(buffer)
					Player.X = Double.read(buffer)
					Player.Y = Double.read(buffer)
					Player.Z = Double.read(buffer)
					Player.Pitch = 1 / UnsignedByte.read(buffer)
					Player.Yaw = 1 / UnsignedByte.read(buffer)
					print('0x04 данные получены!')

				elif PacketID == 0x1A:
					data = Json.read(buffer)
					print(data['translate'])

				elif PacketID == 0x35 or PacketID == 0x3D:
					self.send_raw(0x04, (VarInt, 0)) # Respawn

				elif PacketID == 0x52: # Update Health
					Health = Float.read(buffer)
					if Health == 0:
						self.send_raw(0x04, (VarInt, 0)) # Respawn

			# except (ValueError, timeout, struct.error):
			# 	continue
			except timeout:
				pass

			except Exception as e:
				print('ОШИБКА:', e)
				print(type(e))
				self.active = False

	# def send(self, buffer, packid):
	# 	# zlib.compress()
	# 	PACK(buffer)
	# 	buffer.seek(0)
	# 	types.VarInt.write(packid,buffer)
	# 	PACK(buffer,0)
	# 	PACK(buffer)
	# 	self.socket.sendall(buffer.bytes)

	# def recv(self):
	# 	while True:
	# 		try:
	# 			data = self.socket.recv(1024*128)
	# 		except ConnectionAbortedError:
	# 			self.run = False
	# 			raise Exception('Соединение разорвано')
	# 		if not data:
	# 			self.run = False
	# 			raise Exception('Сервер перестал отвечать')

	# 		buffer = PacketBuffer(data)
	# 		buffer.seek(0)
	# 		size = types.VarInt.read(buffer)
	# 		max_size = types.VarInt.read(buffer)
	# 		if max_size == 0:
	# 			packid = types.VarInt.read(buffer)
	# 			if packid == 0x0E:
	# 				data = types.Json.read(buffer)
	# 				byte = buffer.read(1)
	# 				uuid = types.UUID.read(buffer)
	# 				if self.listen_chat != None:
	# 					self.listen_chat(data,byte,uuid)

	# 			if packid == 0x1F:
	# 				KA = types.Long.read(buffer)
	# 				# print(f'Сохранение соединения: {KA}')
	# 				buffer = PacketBuffer()
	# 				types.Long.write(KA,buffer)
	# 				self.send(buffer,0x10)
	# 		else:
	# 			pass