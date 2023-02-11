from mcc import *

addr = ('fonih.aternos.me', 56943)
username = 'Bot'

main = Main()
main.connect(addr, username)

while main.active:
	msg = input()

	if not msg:
		continue

	elif msg.startswith('\\'):
		msg = msg[1:]

		if msg == 'exit':
			exit()

		elif msg == 'r':
			main.send(0x04, 0) # respawn

		elif msg == 'p' and player.x != None:
			player.y += 1
			main.send(0x12, player.x, player.y, player.z, player.yaw, player.pitch, True)

	else:
		main.send(0x03, msg)

	# https://wiki.vg/Chat#Processing_chat
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Chat_Message_.28serverbound.29