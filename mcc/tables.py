from colorama import Fore
from .types import *

color_name = {
	'black': Fore.BLACK, 
	'red': Fore.RED,
	'green': Fore.GREEN,
	'yallow': Fore.YELLOW,
	'blue': Fore.BLUE,
	'magenta': Fore.MAGENTA,
	'cyan': Fore.CYAN,
	'white': Fore.WHITE,
	'reset': Fore.RESET
}

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

# формат данных для отправки на сервер
dataformat = {
	'send': {
		'login': {
			0x00: [VarInt, String, UnsignedShort, VarInt],
		},

		'tologin': {
			0x00: [String],
		},

		'tostatus': {
			0x00: [],
		},

		'play': {
			0x00: [VarInt],
			0x03: [String],
			0x04: [VarInt],
			0x0F: [Long],
			0x12: [Double, Double, Double, Float, Float, Boolean],
		},
	},

	'recv': {
		'login': {
			0x00: [Json],
			0x02: [UUID, String],
			0x03: [VarInt],
		},

		'status': {
			0x00: [Json],
			0x01: [Long],
			0x1A: [Json],
		},

		'play': {
			0x00: [VarInt, UUID, VarInt, Double, Double, Double, UnsignedByte, UnsignedByte, Int, Short, Short, Short],
			0x1A: [Json],
			0x21: [Long],
			0x38: [Double, Double, Double, Float, Float, Byte, VarInt],
		}
	}
}