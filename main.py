from mcc import *

addr = ('localhost', 25565)
username = 'Bot'

main = Main()
main.connect(addr, username)

while main.active:
	msg = input()
	if msg == 'выход':
		exit()

	elif msg == 'к':
		main.send_raw(0x04, (VarInt, 0)) # respawn

	elif msg.startswith('чат '):
		msg = msg[4:]
		if len(msg) == 0:
			continue

		main.send(0x03, f'String {msg}')

	# https://wiki.vg/Chat#Processing_chat
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Chat_Message_.28serverbound.29