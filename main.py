from mcc import *

addr = ('localhost', 25565)
username = 'Bot'

main = Main()
main.connect(addr, username)

while main.active:
	msg = input()

	if not msg:
		continue

	elif msg.startswith('\\'):
		msg = msg[1:]

		if msg == 'выход':
			exit()

		elif msg == 'к':
			main.send_raw(0x04, (VarInt, 0)) # respawn

		elif msg == 'з' and player.x != None:
			player.y += 1

			main.send(0x12, f'''
				Double {player.x}
				Double {player.y}
				Double {player.z}
				Float {player.yaw}
				Float {player.pitch}
				Boolean True
			''')

	else:
		main.send(0x03, f'String {msg}')

	# https://wiki.vg/Chat#Processing_chat
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Chat_Message_.28serverbound.29