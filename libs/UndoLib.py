import sys
import os
from utils.prettyPrintLib import printColor
from libs.IndexManager import unstageFiles, stageFiles, generateStatus, deleteAddedFiles
from libs.BranchingManager import deleteBranch, createBranch, checkoutSnapshot, deleteTag, createTag, resetToSnapshot
from libs.BasicUtils import getResource, dumpResource
import shutil

def restoreResource(index, resource_name):
    oldResource = getResource(resource_name, specificPath=os.path.join(".cookie", "cache", "undo_cache", str(index)))
    dumpResource(resource_name, oldResource)

def getCacheContent(index, resource_name):
    with open(os.path.join(".cookie", "cache", "undo_cache", str(index), resource_name), "r") as cacheFile:
        cacheContent = cacheFile.read()
    return cacheContent
        

def clearCache(index):
    try:
        shutil.rmtree(os.path.join(".cookie", "cache", "undo_cache", str(index)))
    except FileNotFoundError:
        pass
def undoCommand(args):
    history=getResource("history")
    if history["index"]==0 :
        printColor("Nothing to undo...", "red")
        sys.exit(1)
    if args.index!=None:
        num_check=int(args.index)
        if num_check not in range(0, int(history["index"])):
            printColor("Invalid index {}".format(num_check), "red")
            printColor("Maximum index is {}".format(history["index"]), "red")
        indexToUndo=args.index
    else:
        indexToUndo=str(history["index"])

    prevArgs=history["commands"][indexToUndo] #to do, format specific command for each thing
    printColor("Undoing '{}'".format(prevArgs), "cyan")
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
    elif prevArgs["command"] == 'create_tag':
        undo_create_tag(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'delete_tag':
        undo_delete_tag(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'merge':
        undo_merge(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'login':
        undo_login(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'rconfig':
        undo_rconfig(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'pull':
        undo_pull(prevArgs, indexToUndo)
    elif prevArgs["command"] == 'fetch':
        undo_fetch(prevArgs, indexToUndo)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)
    del history["commands"][indexToUndo]
    history["index"]-=1
    dumpResource("history", history)
    

def undo_add(args, indexToUndo):
    unstageFiles(list(args["paths"]))
    restoreResource(indexToUndo, "staged")
    clearCache(indexToUndo)

def undo_remove(args, indexToUndo):
    stageFiles(list(args["paths"]))
    restoreResource(indexToUndo, "staged")
    clearCache(indexToUndo)

def undo_checkout(args,indexToUndo):
    oldHead = getResource("head", specificPath=os.path.join(".cookie", "cache", "undo_cache", str(indexToUndo)))
    if oldHead["name"]=='DETACHED':
        checkoutSnapshot(None, specRef=oldHead["hash"], reset=args["r"], force=args["f"])
    else:
        checkoutSnapshot(None, specRef=oldHead["name"], reset=args["r"], force=args["f"])
    restoreResource(indexToUndo, "staged")
    try:
        shutil.rmtree(os.path.join(".cookie", "cache", "index_cache"))
    except FileNotFoundError:
        pass
    #os.makedirs(os.path.join(".cookie", "cache", "index_cache"), exist_ok=True)
    try:
        shutil.move(os.path.join(".cookie", "cache", "undo_cache", indexToUndo, "index_cache"), os.path.join(".cookie", "cache"))
    except:
        pass
    clearCache(indexToUndo)

def undo_create_branch(args,indexToUndo):
    deleteBranch(args["branch"])
    if args["c"]:
        oldHead = getResource("head", specificPath=os.path.join(".cookie", "cache", "undo_cache", str(indexToUndo)))
        if oldHead["name"]=='DETACHED':
            checkoutSnapshot(None, specRef=oldHead["hash"])
        else:
            checkoutSnapshot(None, specRef=oldHead["name"])
        try:
            shutil.rmtree(os.path.join(".cookie", "cache", "index_cache"))
        except FileNotFoundError:
            pass
        #os.makedirs(os.path.join(".cookie", "cache", "index_cache"), exist_ok=True)
        try:
            shutil.move(os.path.join(".cookie", "cache", "undo_cache", indexToUndo, "index_cache"), os.path.join(".cookie", "cache"))
        except:
            pass
        restoreResource(indexToUndo, "staged")
    clearCache(indexToUndo)

def undo_delete_branch(args,indexToUndo):
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "branches")
    #os.makedirs(undoCachePath, exist_ok=True)
    with open(os.path.join(undoCachePath, args["branch"]), "r") as deletedBranchFile:
        sha=deletedBranchFile.read().strip()
    createBranch(args["branch"], currentRef=False, ref=sha)

def undo_create_tag(args,indexToUndo):
    deleteTag(args["tag"])
    if args["c"]:
        oldHead = getResource("head", specificPath=os.path.join(".cookie", "cache", "undo_cache", str(indexToUndo)))
        if oldHead["name"]=='DETACHED':
            checkoutSnapshot(None, specRef=oldHead["hash"])
        else:
            checkoutSnapshot(None, specRef=oldHead["name"])
        try:
            shutil.rmtree(os.path.join(".cookie", "cache", "index_cache"))
        except FileNotFoundError:
            pass
        #os.makedirs(os.path.join(".cookie", "cache", "index_cache"), exist_ok=True)
        try:
            shutil.move(os.path.join(".cookie", "cache", "undo_cache", indexToUndo, "index_cache"), os.path.join(".cookie", "cache"))
        except:
            pass
        restoreResource(indexToUndo, "staged")
    clearCache(indexToUndo)

def undo_delete_tag(args,indexToUndo):
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "tags")
    #os.makedirs(undoCachePath, exist_ok=True)
    with open(os.path.join(undoCachePath, args["tag"]), "r") as deletedTagFile:
        sha=deletedTagFile.read().strip()
    createTag(args["tag"], currentRef=False, ref=sha, checkout = False)

def undo_login(args,indexToUndo):
    restoreResource(indexToUndo, "userdata")
    clearCache(indexToUndo)

def undo_merge(args, indexToUndo):
    restoreResource(indexToUndo, "refs")
    restoreResource(indexToUndo, "head")
    restoreResource(indexToUndo, "logs")
    restoreResource(indexToUndo, "staged")
    restoreResource(indexToUndo, "index")
    head = getResource("head")
    checkoutSnapshot(None, specRef=head["name"], reset=True, force=True)
    generateStatus(None, quiet=True)
    deleteAddedFiles()
    new_commit = getCacheContent(indexToUndo, "new_commit")
    os.remove(os.path.join(".cookie", "objects", new_commit[:2], new_commit[2:]))
    clearCache(indexToUndo)

def undo_commit(args, indexToUndo):
    restoreResource(indexToUndo, "refs")
    restoreResource(indexToUndo, "head")
    restoreResource(indexToUndo, "logs")
    restoreResource(indexToUndo, "staged")
    restoreResource(indexToUndo, "index")
    try:
        new_commit = getCacheContent(indexToUndo, "new_commit")
        os.remove(os.path.join(".cookie", "objects", new_commit[:2], new_commit[2:]))
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(os.path.join(".cookie", "cache", "index_cache"))
    except FileNotFoundError:
        pass
    #os.makedirs(os.path.join(".cookie", "cache", "index_cache"), exist_ok=True)
    try:
        shutil.move(os.path.join(".cookie", "cache", "undo_cache", indexToUndo, "index_cache"), os.path.join(".cookie", "cache"))
    except:
        pass
    clearCache(indexToUndo)

def undo_rconfig(args, indexToUndo):
    restoreResource(indexToUndo, "remote_config")
    clearCache(indexToUndo)

def undo_pull(args, indexToUndo):
    restoreResource(indexToUndo, "refs")
    restoreResource(indexToUndo, "logs")
    clearCache(indexToUndo)

def undo_fetch(args, indexToUndo):
    restoreResource(indexToUndo, "refs")
    restoreResource(indexToUndo, "logs")
    clearCache(indexToUndo)