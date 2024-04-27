import sys
import os
from utils.prettyPrintLib import printColor
from libs.IndexManager import unstageFiles, stageFiles
from libs.BranchingManager import deleteBranch, createBranch, checkoutSnapshot
from libs.BasicUtils import getResource, dumpResource
import shutil


def restoreResource(index, resource_name):
    oldResource = getResource(resource_name, specificPath=os.path.join(".cookie", "cache", "undo_cache", str(index)))
    dumpResource(resource_name, oldResource)
    shutil.rmtree(os.path.join(".cookie", "cache", "undo_cache", str(index)))

def undoCommand(args):
    history=getResource("history")
    if args.index!=None:
        num_check=int(args.index)
        if num_check not in range(0, int(history["index"])):
            printColor("Invalid index {}".format(num_check), "red")
            printColor("Maximum index is {}".format(history["index"]), "red")
        indexToUndo=args.index
    else:
        indexToUndo=str(history["index"])

    prevArgs=history["commands"][indexToUndo] #to do, format specific command for each thing
    printColor("Undoing '{}'".format(prevArgs), "blue")
    if prevArgs["command"] == 'add':
        undo_add(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'remove':
        undo_remove(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'commit':
        undo_commit(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'checkout':
        undo_checkout(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'create_branch':
        undo_create_branch(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'delete_branch':
        undo_delete_branch(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'merge':
        undo_merge(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'login':
        undo_login(prevArgs, indexToUndo)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)
    del history["commands"][indexToUndo]
    history["index"]-=1
    dumpResource("history", history)
    

def undo_add(args, indexToUndo):
    unstageFiles(list(args["paths"]))
    restoreResource(indexToUndo, "staged")

def undo_remove(args, indexToUndo):
    stageFiles(list(args["paths"]))
    restoreResource(indexToUndo, "staged")

def undo_checkout(args,indexToUndo):
    checkoutSnapshot(args["ref"])

def undo_create_branch(args,indexToUndo):
    deleteBranch(args["branch"])

def undo_delete_branch(args,indexToUndo):
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "branches")
    os.makedirs(undoCachePath, exist_ok=True)
    with open(os.path.join(undoCachePath, args["branch"]), "r") as deletedBranchFile:
        sha=deletedBranchFile.read().strip()
    createBranch(args["branch"], currentRef=False, ref=sha)


def undo_login(args,indexToUndo):
    restoreResource(indexToUndo, "userdata")

def undo_merge(args):
    pass

def undo_commit(args, indexToUndo):
    pass
