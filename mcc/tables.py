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