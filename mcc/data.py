from .tables import func_name, func_type, dataformat
from io import BytesIO

class Buffer:
	def __init__(self,data=None):
		self.bytes_ = BytesIO()
		if data is not None:
			self.bytes_.write(data)

	def write(self, value):
		return self.bytes_.write(value)

	def read(self, length=None):
		return self.bytes_.read(length)

	def clear(self):
		self.bytes_ = BytesIO()

	def reset_cursor(self):
		self.bytes_.seek(0)

	def seek(self,index,end=False):
		if end:
			self.bytes_.seek(len(self.bytes) - index)
		else:
			self.bytes_.seek(index)

	def pack(self, func, value):
		data = self.bytes
		self.clear()
		func.write(value, self)
		self.write(data)

	def __len__(self):
		return len(self.bytes)

	@property
	def bytes(self):
		return self.bytes_.getvalue()

	# Hex representation of bytes array
	def __str__(self):
		return ' '.join(["%02X" % b for b in self.bytes_.getvalue()])


class Packet(list):
	def __init__(self, _id, *args, **kwargs):
		super().__init__(args, **kwargs)
		self.id = _id
		
	def to_buffer(self, state='play'):
		return to_buffer(self.id, self, state=state)

def to_buffer(_id, args, state='play'):
	levelformat = dataformat['send'][state]

	if len(args) != len(levelformat[_id]):
		raise Exception(f'неверное количество аргументов (ожидалось {len(levelformat[_id])}, имеется {len(args)})')

	buffer = Buffer()
	for func, data in zip(levelformat[_id], args):
		if func.__name__ not in func_type:
			raise Exception(f'не зарегистрированный тип данных ({func.__name__})')

		if type(data) != func_type[func.__name__]:
			raise Exception(f'неверный тип данных (ожидался {func_type[func.__name__]}, имеется {type(data)})')

		func.write(data, buffer)
	return buffer

	# def send_raw(self, packid, *args):
	# 	buffer = PacketBuffer()
	# 	for func, value in args:
	# 		func.write(value, buffer)

	# 	PACK(buffer)
	# 	buffer.seek(0)
	# 	VarInt.write(packid, buffer)
	# 	if self.State == 'play' and self.Threshold >= 0:
	# 		PACK(buffer, 0)
	# 	PACK(buffer)
	# 	self.socket.send(buffer.bytes)


	# def send(self, packid, text, *args):
	# 	text = text.replace('\t', '')
	# 	args = list(args)
	# 	if ';' in text: p = ';'
	# 	else: p = '\n'

	# 	for line in text.split(p):
	# 		if not line:
	# 			continue

	# 		name, value = line.split(' ', 1)
	# 		name.replace(' ', '')
	# 		if value[0] == '%':
	# 			value = self.data[value[1:]]

	# 		func = func_name[name]
	# 		_type = func_type[name]
	# 		value = _type(value)

	# 		args.append((func, value))
	# 	self.send_raw(packid, *args)

def from_buffer(id, buffer):
	levelformat = dataformat['recv']
	res = []
	for func in levelformat[id]:
		try:
			res.append(func.read(buffer))
		except Exception as e:
			print(buffer.bytes)
			print(hex(id), func)
			raise e
	return res

	# def read_uncompressed(self, buffer):
	# 	length = VarInt.read(buffer)
	# 	id = VarInt.read(buffer)
	# 	return length, id

	# def read(self, buffer, text):
	# 	res = []
	# 	for name in text.split(' '):
	# 		count = 1
	# 		if '%' in name:
	# 			count, name = name.split('%')
	# 			count = int(count)

	# 		if name not in func_name:
	# 			continue

	# 		func = func_name[name]

	# 		for _ in range(count):
	# 			res.append(func.read(buffer))
	# 	return res