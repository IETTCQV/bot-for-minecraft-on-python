from mcc import *

# iepc.hopto.org
addr = ('localhost', 25565)
username = 'Bot'

main = Main()
main.connect(addr, username)
chat_color = True

# прослушивание чата
def listen_chat(data, byte, uuid):
	text = ''
	if 'extra' in data:
		for obj in data['extra']:
			if chat_color and 'color' in obj:
				text += colorama.text(obj['text'],obj['color'])
			else:
				text += obj['text']
	else:
		text = data
	print(text)

main.listen_chat = listen_chat

# Сообщения в чат
while main.active:
	message = input()
	if message == 'exit':
		exit()

	elif message == 'r':
		main.send_raw(0x04, (VarInt, 0))

	elif message == 'p':
		main.send(0x14, 'Boolean True')

	elif message in ['w', 'a', 's', 'd']:
		if Player.X is None:
			continue

		if message == 'w':
			Player.X += 1
		elif message == 's':
			Player.X -= 1
		elif message == 'd':
			Player.Z += 1
		elif message == 'a':
			Player.Z -= 1

		main.send(0x11, f"""
			Double {Player.X}
			Double {Player.Y}
			Double {Player.Z}
			Boolean True
		""")
		# main.send(0x14, 'Boolean True')

		print('поппытка перемещения')

	# if message:
	# 	buffer = PacketBuffer()
	# 	types.String.write(message,buffer)
	# 	main.send(buffer,0x03)