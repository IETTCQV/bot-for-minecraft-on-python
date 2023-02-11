from colorama import just_fix_windows_console, Fore, Back, Style
from time import localtime
just_fix_windows_console()

def error(self, text):
	self.running = False
	t = localtime()
	print(Fore.RED + f'[{t.tm_hour}:{t.tm_min}:{t.tm_sec}] Критическая ошибка: ' + text + Fore.RESET)