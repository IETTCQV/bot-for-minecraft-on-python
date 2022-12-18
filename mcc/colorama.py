import ctypes
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

codes = {
	'dark_red':[31,41],
	'red':[91,101],

	'gold':[33,43],
	'yellow':[93,103],

	'dark_green':[32,42],
	'green':[92,102],

	'aqua':[96,106],
	'dark_aqua':[36,46],
	'dark_blue':[34,44],
	'blue':[94,104],
	
	'light_purple':[95,105],
	'dark_purple':[35,45],

	'white':[1,107],
	'gray':[0,47],
	'dark_gray':[90,100],
	'black':[30,40],

	'underline':4,
	'invert':7}

def text(text='',color='white',fon='black',reset=True):
	if text:
		if color == 'black' and fon == 'black':
			fon = 'dark_gray'
		out_text = ''
		#if color != None and color != 'gray':
		out_text += f'\033[{codes[color][0]}m'
		out_text += f'\033[{codes[fon][1]}m'
		out_text += text
		out_text += (f'\033[0m' if reset else '')
		return out_text
	return ''

if __name__ == '__main__':
	for name in list(codes.keys())[:-2]:
		print(f'{name} == {text("Test",name)}')
