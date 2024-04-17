import curses
from curses import wrapper
from libs.objectLib.ObjectManager import load
import os
from utils.prettyPrintLib import printColor
from time import ctime
from libs.BasicUtils import getResource, dumpResource


def logCommit(commitObject):
    logs=getResource("logs")
    commitHash=commitObject.getHash()
    edgesFromCommit=[]
    for parent in commitObject.parents:
        logs["edge_index"]+=1
        logs["edges"][logs["edge_index"]] = {"from": commitHash, "to": parent}
        edgesFromCommit.append(logs["edge_index"])
    logs["adj"][commitHash]=edgesFromCommit
    logs["nodes"].append(commitHash)
    dumpResource("logs", logs)

def printCommitData(hash):
    commit = load(hash, os.path.join('.cookie', 'objects'))
    printColor("---------------------------------------------------------------------", "white")
    printColor("     <> Commit : {}".format(commit.getHash()), "white")
    printColor("        '{}'".format(commit.message), "white")
    print     ("                                                                              ")
    printColor("  Author       : {}".format(commit.author), "white")
    printColor("  Committed at : {}".format(ctime(float(commit.time))), "white")
    printColor("  Snapshot     : {}".format(commit.snapshot), "white")
    printColor("---------------------------------------------------------------------", "white")

def getAncestors(hash, acc, logs):
    acc.append(hash)
    for edge in logs["adj"][hash]:
        getAncestors(logs[str(edge)]["to"], acc, logs)
    

# @wrapper
# def logCommits(stdscr, hash):
#     commit=load(hash, os.path.join(".cookie", "objects"))

#     stdscr.clear()
#     stdscr.addstr(3, 3, "Current Commit Hash: {}".format(commit.getHash()))
#     stdscr.refresh()
#     stdscr.getch()

# #logCommits(hash='42c8f315c872ac0b81897280fd4feb9713147c7e')