
'''
with open('mcc/types.py', 'r') as file:
	text = file.read()

for line in text.split('class '):
	name = line.split(':')[0]
	if '(Type)' in name:
		name = name[:-6]
		print(f"	'{name}': {name},")
'''

'''
import yaml
import os

def send_packet(name):
	name += '.yaml'
	path = 'packet/'+name

	if name not in os.listdir('packet'):
		raise Exception('пакет не обнаружен')

	with open(path, 'r') as file:
		text = file.read()
		data = yaml.safe_load(text)
'''

print(1024**2*2)