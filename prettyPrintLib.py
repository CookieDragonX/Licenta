from termcolor import colored, cprint
from sys import exit

def printColor(message, color):
    if color not in ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white' ]:
        exit(1)
    print(colored(message, color=color))
