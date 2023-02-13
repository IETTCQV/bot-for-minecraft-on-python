from socket import socket as Socket, AF_INET, SOCK_STREAM
from colorama import just_fix_windows_console, Fore, Back, Style
from time import localtime, sleep, time, strftime
import json
import struct
import uuid
import os

just_fix_windows_console()

def get_date():
	return strftime('%d.%m.%Y', localtime())

def get_time():
	return strftime('%H:%M:%S', localtime())

_print = print
def print(*args, **kwargs):
	_print(f'[{get_time()}]', *args, **kwargs)

def info(text):
	_print(Fore.GREEN + f'[{get_time()}] ' + text + Fore.RESET)

def warn(text):
	_print(Fore.YELLOW + f'[{get_time()}] ' + text + Fore.RESET)

def error(text):
	_print(Fore.RED + f'[{get_time()}] ' + text + Fore.RESET)
	os.system('pause')
	exit()


class Type:
	__slots__ = ()

	@staticmethod
	def read(stream):
		raise NotImplementedError("Base data type not de-serializable")

	@staticmethod
	def write(value, stream):
		raise NotImplementedError("Base data type not serializable")


class UnsignedShort(Type):
	@staticmethod
	def read(data, index):
		return struct.unpack('>H', data[index:index+2])[0], index + 2

	@staticmethod
	def write(value):
		return struct.pack('>H', value)


class VarInt(Type):
	@staticmethod
	def read(data, index):
		number = 0
		bytes_encountered = 0
		while True:
			byte = data[index + bytes_encountered]
			number |= (byte & 0x7F) << 7 * bytes_encountered
			bytes_encountered += 1

			if not byte & 0x80:
				break

			if bytes_encountered > 5:
				raise ValueError("Tried to read too long of a VarInt")
		return number, index + bytes_encountered

	@staticmethod
	def write(value):
		out = bytes()
		while True:
			byte = value & 0x7F
			value >>= 7
			out += struct.pack("B", byte | (0x80 if value > 0 else 0))
			if value == 0:
				break
		return out


class String(Type):
	@staticmethod
	def read(data, index):
		length, index = VarInt.read(data, index)
		return data[index:index+length].decode("utf-8"), index + length

	@staticmethod
	def write(value):
		value = value.encode('utf-8')
		return VarInt.write(len(value)) + value


class Json(Type):
	@staticmethod
	def read(data, index):
		length, index = VarInt.read(data, index)
		return json.loads(data[index:index+length]), index + length

	@staticmethod
	def write(value):
		value = json.dumps(value).encode('utf-8')
		return VarInt.write(len(value)) + value


class SimpleBot:
	addr = None 
	name = None
	socket = None

	connected = False
	size = 1024*16

	def __init__(self, addr, name='SimpleBot'):
		self.addr = addr
		self.name = name

		self.b1 = bytes()
		self.b1 += VarInt.write(758)
		self.b1 += String.write(addr[0])
		self.b1 += UnsignedShort.write(addr[1])
		self.b1 += VarInt.write(2)

		self.b1 = VarInt.write(0) + self.b1
		self.b1 = VarInt.write(len(self.b1)) + self.b1


		self.b2 = bytes()
		self.b2 += String.write(name)

		self.b2 = VarInt.write(0) + self.b2
		self.b2 = VarInt.write(len(self.b2)) + self.b2

		# print(self.b1, self.b2)

	def close(self):
		if self.socket != None:
			try: self.socket.close()
			except: pass
			self.socket = None
		self.connected = False

	def connect(self):
		self.close()
		self.socket = Socket(AF_INET, SOCK_STREAM)
		self.socket.settimeout(15)
		try:
			self.socket.connect(self.addr)
		except Exception as e:
			warn(f'SimpleBot.connect: {e}')
			self.close()

	def _connect(self):
		t = time()
		while self.socket is None:
			self.connect()
			if time() - t >= 60:
				error('бот не смог подключиться')

	def run(self):
		self.main()

	def main(self):
		while True:
			try:
				while True:
					if self.socket is None:
						self._connect()

					if not self.connected:
						self.socket.send(self.b1)
						sleep(0.1)
						self.socket.send(self.b2)
						self.connected = True

					data = self.socket.recv(self.size)
					if not data:
						warn('Сервер перестал отвечать')
						self.close()
						continue

					try:
						length, index = VarInt.read(data, 0)
						length_data, index = VarInt.read(data, index)
					except:
						continue

					if length_data == 0:
						id, index = VarInt.read(data, index)

						if id == 0x21:
							data = data[:index-1] + b'\x0F' + data[index:]
							# 0 1 2 3 4 5 6 7 8 9 10 11
							# Д Д А Л Л Л Л Л Л Л Л  Л
							# print(data)
							self.socket.send(data)
							info(f'keep Alive ID')

						elif id == 0x1A:
							data, index = Json.read(data, index)
							# {'text': '§7Hello §aSimpleBot§7!\n§8You are trying to connect to fonih.aternos.me.\n\n§4This server is offline.\n§7§lAD§r§7: §fOnly pay to play: §acraft.link/ea'}
							# {'translate': 'disconnect.genericReason', 'with': ['Internal Exception: io.netty.handler.codec.DecoderException: java.io.IOException: Packet 0/22 (PacketPlayInBoatMove) was larger than I expected, found 4 bytes extra whilst reading packet 22']}
							if 'text' in data and 'This server is offline.' in data['text']:
								error('Aternos: сервер выключен')
							elif 'with' in data:
								warn(f'SimpleBot.main: {data["with"][0]}')
							else:
								warn(f'SimpleBot.main: {data}')
							self.close()
							continue

			except Exception as e:
				warn(f'SimpleBot.main: {e}')
				self.close()
					
if __name__ == '__main__':
	name = __file__.split('\\')[-1]
	if '.' in name:
		name = name.split('.')[0] + '.json'

	if not os.path.isfile(name):
		error(f'Нет файла настроек ({name})')

	with open(name, 'rb') as file:
		data = file.read()

	try:
		config = json.loads(data)
		for k, i in zip(['host', 'port', 'name'], ['хосте', 'порте', 'имени']):
			if k not in config:
				raise Exception('нет информации о '+i)

		for k, t in zip(['host', 'port', 'name'], [str, int, str]):
			if type(config[k]) != t:
				raise Exception(f'неверный тип данных {k}: {type(config[k])}, требуется: {t}')

	except Exception as e:
		error(f'ошибка чтения настроек: {e}')

	sb = SimpleBot((config['host'], config['port']), config['name'])
	sb.run()