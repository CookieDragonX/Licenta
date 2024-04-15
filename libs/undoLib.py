import sys
import os
from utils.prettyPrintLib import printColor
from libs.IndexManager import unstageFiles, stageFiles
from libs.BranchingManager import deleteBranch, createBranch
from libs.BasicUtils import getResource, dumpResource

def undoCommand(args):
    history=getResource("history")
    if args.index!=None:
        num_check=int(args.index)
        if num_check not in range(0, int(history["index"])):
            printColor("Invalid index {}".format(num_check), "red")
            printColor("Maximum index is {}".format(history["index"]))
        indexToUndo=args.index
    else:
        indexToUndo=str(history["index"])

    prevArgs=history["commands"][indexToUndo] #to do, format specific command for each thing
    printColor("Undoing '{}'".format(prevArgs), "blue")
    if prevArgs["command"] == 'add':
        undo_add(prevArgs)
    elif prevArgs["command"] == 'remove':
        undo_remove(prevArgs)
    elif prevArgs["command"] == 'commit':
        undo_commit(prevArgs)
    elif prevArgs["command"] == 'checkout':
        undo_checkout(prevArgs)
    elif prevArgs["command"] == 'create_branch':
        undo_create_branch(prevArgs)
    elif prevArgs["command"] == 'delete_branch':
        undo_delete_branch(prevArgs)
    elif prevArgs["command"] == 'login':
        undo_login(prevArgs)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)
    del history["commands"][indexToUndo]
    history["index"]-=1
    dumpResource("history", history)
    

def undo_add(args):
    unstageFiles(list(args["paths"]))

def undo_remove(args):
    stageFiles(list(args["paths"]))

def undo_commit(args):
    pass

def undo_checkout(args):
    pass

def undo_create_branch(args):
    deleteBranch(args["branch"])

def undo_delete_branch(args):
    undoCachePath=os.path.join(".cookie", "undo_cache", "branches")
    os.makedirs(undoCachePath, exist_ok=True)
    with open(os.path.join(undoCachePath, args["branch"]), "w") as deleteBranchFile:
        sha=deleteBranchFile.read().strip()
    createBranch(args["branch"], currentRef=False, ref=sha)


def undo_login(args):
    pass