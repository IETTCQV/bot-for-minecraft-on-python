import struct
import uuid
import json

# Типы данных Java
class Type:
	__slots__ = ()

	@staticmethod
	def read(stream):
		raise NotImplementedError("Base data type not de-serializable")

	@staticmethod
	def write(value, stream):
		raise NotImplementedError("Base data type not serializable")


class Boolean(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('?', stream.read(1))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('?', value))


class UnsignedByte(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>B', stream.read(1))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>B', value))


class Byte(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>b', stream.read(1))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>b', value))


class Short(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>h', stream.read(2))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>h', value))


class UnsignedShort(Type):
	@staticmethod
	def read(data, index):
		return struct.unpack('>H', data[index:index+2])[0], index + 2

	@staticmethod
	def write(value):
		return struct.pack('>H', value)


class Int(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>i', stream.read(4))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>i', value))


class FixedPointInteger(Type):
	@staticmethod
	def read(stream):
		return Int.read(stream) / 32

	@staticmethod
	def write(value, stream):
		return Int.write(int(value * 32), stream)


class VarInt(Type):
	@staticmethod
	def read(data, index):
		number = 0
		# Limit of 5 bytes, otherwise its possible to cause
		# a DOS attack by sending VarInts that just keep
		# going
		bytes_encountered = 0
		while True:
			byte = data[index + bytes_encountered]
			# if len(byte) < 1:
			# 	raise EOFError("Unexpected end of message.")

			# byte = ord(byte)
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

	@staticmethod
	def size(value):
		for max_value, size in VARINT_SIZE_TABLE.items():
			if value < max_value:
				return size
		raise ValueError("Integer too large")


# Maps (maximum integer value -> size of VarInt in bytes)
VARINT_SIZE_TABLE = {
	2 ** 7: 1,
	2 ** 14: 2,
	2 ** 21: 3,
	2 ** 28: 4,
	2 ** 35: 5,
	2 ** 42: 6,
	2 ** 49: 7,
	2 ** 56: 8,
	2 ** 63: 9,
	2 ** 70: 10,
	2 ** 77: 11,
	2 ** 84: 12
}


class Long(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>q', stream.read(8))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>q', value))


class UnsignedLong(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>Q', stream.read(8))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>Q', value))


class Float(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>f', stream.read(4))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>f', value))


class Double(Type):
	@staticmethod
	def read(stream):
		return struct.unpack('>d', stream.read(8))[0]

	@staticmethod
	def write(value, stream):
		return stream.write(struct.pack('>d', value))


class VarIntArray(Type):
	@staticmethod
	def read(stream):
		count = VarInt.read(stream)
		arr = []
		for _ in range(0, count):
			arr.append(VarInt.read(stream))
		return arr

	@staticmethod
	def write(values, stream):
		size = 0
		for value in values:
			size += VarInt.write(value, stream)
		return size


class ShortPrefixedByteArray(Type):
	@staticmethod
	def read(stream):
		length = Short.read(stream)
		return struct.unpack(str(length) + "s", stream.read(length))[0]

	@staticmethod
	def write(value, stream):
		return Short.write(len(value), stream) + stream.write(value)


class VarIntPrefixedByteArray(Type):
	@staticmethod
	def read(stream):
		length = VarInt.read(stream)
		return struct.unpack(str(length) + "s", stream.read(length))[0]

	@staticmethod
	def write(value, stream):
		return VarInt.write(len(value), stream) + stream.write(struct.pack(str(len(value)) + "s", value))


class TrailingByteArray(Type):
	""" A byte array consisting of all remaining data. If present in a packet
		definition, this should only be the type of the last field. """

	@staticmethod
	def read(stream):
		return stream.read()

	@staticmethod
	def write(value, stream):
		return stream.write(value)


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

class UUID(Type):
	@staticmethod
	def read(stream):
		return str(uuid.UUID(bytes=stream.read(16)))

	@staticmethod
	def write(value, stream):
		return stream.write(uuid.UUID(value).bytes)