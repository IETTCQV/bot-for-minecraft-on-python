from mcc import *

bot = Bot()
bot.run(('fonih.aternos.me', 56943), 'Bot')

while bot.running:
	msg = input()

	if not msg:
		continue

	elif msg.startswith('\\'):
		msg = msg[1:]

		if msg == 'exit':
			exit()

		elif msg == 'r':
			bot.send(0x04, 0) # respawn

		elif msg == 'p' and player.x != None:
			player.y += 1
			bot.send(0x12, player.x, player.y, player.z, player.yaw, player.pitch, True)

	else:
		bot.send(0x03, msg)

	# https://wiki.vg/Chat#Processing_chat
	# https://wiki.vg/index.php?title=Protocol&oldid=17499#Chat_Message_.28serverbound.29