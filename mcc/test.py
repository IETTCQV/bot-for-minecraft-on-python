
text = b'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"yellow","text":"IvanExe joined the game"}],"text":""}'

import json

#json.loads()

de = {
	'extra':
		[
			{
				'bold': False,
				'italic': False,
				'underlined': False,
				'strikethrough': False,
				'obfuscated': False,
				'color': 'yellow',
				'text': 'IvanExe joined the game'
			}
		],
	'text': ''
	}

print(json.dumps(de).encode())