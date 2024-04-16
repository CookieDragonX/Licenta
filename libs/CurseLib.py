import curses
from curses import wrapper
from libs.objectLib.ObjectManager import load
import os
@wrapper
def logCommits(stdscr, hash):
    commit=load(hash, os.path.join(".cookie", "objects"))

    stdscr.clear()
    stdscr.addstr(3, 3, "Current Commit Hash: {}".format(commit.getHash()))
    stdscr.refresh()
    stdscr.getch()

logCommits(hash='42c8f315c872ac0b81897280fd4feb9713147c7e')