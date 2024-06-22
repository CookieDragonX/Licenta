from termcolor import colored
import colorama
from sys import exit
import os
import sys

def printColor(message, color):
    if color not in ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white' ]:
        print("[DEV ERROR][printColor] Color not defined.")
        sys.exit(1)
    if os.name=='nt':
        colorama.init()

    print(colored(message, color=color))

