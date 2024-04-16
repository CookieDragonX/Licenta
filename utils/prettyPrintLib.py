from termcolor import colored
import colorama
from sys import exit
import os

def printColor(message, color):
    if color not in ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white' ]:
        exit(1)
    if os.name=='nt':
        colorama.init()
    print(colored(message, color=color))
