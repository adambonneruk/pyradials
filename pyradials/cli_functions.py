import os

def banner(version:str = '0.0.0'):
	os.system("cls")
	print('\n  ____        ____           _ _       _        ')
	print(' |  _ \ _   _|  _ \ __ _  __| (_) __ _| |___    ')
	print(' | |_) | | | | |_) / _` |/ _` | |/ _` | / __|   ')
	print(' |  __/| |_| |  _ < (_| | (_| | | (_| | \__ \  v%s' % version)
	print(' |_|    \__, |_| \_\__,_|\__,_|_|\__,_|_|___/  by Adam Bonner')
	print('        |___/                                  MIT Licence, 2024\n')

def draw_nice_line():
	terminal_width = os.get_terminal_size().columns
	print("─" * terminal_width)