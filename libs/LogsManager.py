from libs.objectLib.ObjectManager import load
import os
from utils.prettyPrintLib import printColor
from time import ctime
from libs.BasicUtils import getResource, dumpResource

def logCommit(commitObject):
    logs=getResource("logs")
    commitHash=commitObject.getHash()
    edgesFromCommit=[]
    parent = commitObject.parents[0]
    logs["edge_index"]+=1
    logs["edges"][logs["edge_index"]] = {"from": commitHash, "to": parent}
    edgesFromCommit.append(logs["edge_index"])
    logs["adj"][commitHash]=edgesFromCommit
    if parent == "None":
        depth=1
    else:
        depth=int(logs["nodes"][parent])+1
    logs["nodes"][commitHash]=depth
    dumpResource("logs", logs)

def printCommitData(commit):

    printColor("---------------------------------------------------------------------", "white")
    printColor("     <> Commit : {}".format(commit.getHash())                         , "green")
    printColor("        '{}'".format(commit.message), "white")
    print     ("                                                                              ")
    printColor("  Author       : {}".format(commit.author), "white")
    printColor("  Committed at : {}".format(ctime(float(commit.time))), "white")
    printColor("  Snapshot     : {}".format(commit.snapshot), "white")
    printColor("---------------------------------------------------------------------", "white")

def logSequence(args):
    head = getResource("head")
    currentCommit = load(head["hash"], os.path.join('.cookie', 'objects'))
    trackHistory=[]
    key = None
    while key != 'q':
        trackHistory.append(currentCommit)
        printCommitData(currentCommit)
        if len(trackHistory) > 1:
            normalList = ['q', 'n', 'p']
            normalInputStr = "    <> [q] - quit | [n] - next | [p] - prev -->"
            mergeList = ['q', 'b', 'm', 'p']
            mergeInputStr = "    <> [q] - quit | [b] - base | [m] - merged | [p] - prev -->"
        else : 
            normalList = ['q', 'n']
            normalInputStr = "    <> [q] - quit | [n] - next -->"
            mergeList = ['q', 'b', 'm']
            mergeInputStr = "    <> [q] - quit | [b] - base | [m] - merged -->"
        if currentCommit.parents[0] == 'None':
            printColor("This is the first commit, exitting...", "green")
            key = 'q'
        else:
            if len(currentCommit.parents) == 1 or args.b:
                while key not in normalList:
                    print("Please choose a valid option!")
                    key = input(normalInputStr).lower()
            else:
                while key not in mergeList:
                    key = input(mergeInputStr).lower()
        if key == 'q':
            printColor("Stopping log...", "green")
            break        
        elif key == 'n' or key =='b':
            currentCommit = load(currentCommit.parents[0], os.path.join('.cookie', 'objects'))
        elif key == 'm':
            currentCommit = load(currentCommit.parents[1], os.path.join('.cookie', 'objects'))
        elif key == 'p':
            currentCommit = trackHistory[-2]
            trackHistory.pop()
            trackHistory.pop()



# @wrapper
# def logCommits(stdscr, hash):
#     commit=load(hash, os.path.join(".cookie", "objects"))

#     stdscr.clear()
#     stdscr.addstr(3, 3, "Current Commit Hash: {}".format(commit.getHash()))
#     stdscr.refresh()
#     stdscr.getch()

# #logCommits(hash='42c8f315c872ac0b81897280fd4feb9713147c7e')