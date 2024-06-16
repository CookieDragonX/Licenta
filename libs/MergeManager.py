import sys
import os
from libs.objectLib.ObjectManager import store, load, getObjectType
from libs.objectLib.Commit import Commit
from libs.objectLib.Tree import Tree
from libs.objectLib.Blob import Blob
from libs.BranchingManager import getSnapshotFromCommit, updateHead, resetToSnapshot
from libs.BasicUtils import getResource, dumpResource, cacheFile
from utils.prettyPrintLib import printColor
from utils.stringMerge import merge
from time import time, sleep
from libs.LogsManager import logCommit
import subprocess
import shutil, psutil

def _unidiff_output(target, source):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """
    import difflib
    target=target.splitlines(1)
    source=source.splitlines(1)
    diff=difflib.unified_diff(target, source, fromfile='target', tofile='source')
    return ''.join(diff)

def get_proc_status(pid):
    #https://stackoverflow.com/questions/24803272/how-do-i-know-if-a-file-has-been-closed-if-i-open-it-using-subprocess-popen
    """Get the status of the process which has the specified process id."""
    proc_status = None
    try:
        proc_status = psutil.Process(pid).status()
    except psutil.NoSuchProcess as no_proc_exc:
        pass
    except psutil.ZombieProcess as zombie_proc_exc:  
        # For Python 3.0+ in Linux (and MacOS?).
        pass
    return proc_status

def fileEditProcess(path):
    if os.name == "posix":
        editorName = "nano"
    else:
        editorName = "notepad"
    if shutil.which(editorName):
        phandler = subprocess.Popen([editorName, path])
    elif "EDITOR" in os.environ:
        phandler = subprocess.Popen([os.environ["EDITOR"], path])
    pid = phandler.pid
    pstatus = get_proc_status(pid)
    printColor("Currently editting file '{}'...".format(os.path.basename(path)), "green")
    printColor("Save and close oppened file to continue!", "green")
    while pstatus is not None and pstatus != "zombie":
        sleep(1)
        pstatus = get_proc_status(pid)

    if os.name == 'posix' and pstatus == "zombie":   # Handle zombie processes in Linux (and MacOS?).
        print("subprocess %s, near-final process status: %s." % (pid, pstatus))
        phandler.communicate()
    pstatus = get_proc_status(pid)

def mergeSourceIntoTarget(target, source):
    if target == None:
        target = getResource("head")["name"]
    createMergeCommit(target, source)

def mergeBlobs(target, source, base, objectsPath): #the args are hashes
    filename = None
    if target == None and source==None and base == None:
        printColor("[DEV ERROR][mergeBlobs] all args None", "red")
    elif base == None:
        if target == None and source != None:
            return source
        elif target != None and source == None:
            return target
    if target == None:
        targetBlob = Blob(None)
    else:
        targetBlob = load(target, objectsPath)
        if not filename:
            filename=targetBlob.filename
    if source == None:
        sourceBlob = Blob(None)
    else:
        sourceBlob = load(source, objectsPath)
        if not filename:
            filename=sourceBlob.filename
    if base != None:
        baseBlob = Blob(None)
    else:
        baseBlob = load(base, objectsPath)
    
    metaData=[b"B"]
    metaData.append(filename.encode('utf-8'))
    dataIsBinary = False
    try:
        sourceString = sourceBlob.content.decode('utf-8')
    except UnicodeDecodeError:
        dataIsBinary = True
    try:
        targetString = targetBlob.content.decode('utf-8')
    except UnicodeDecodeError:
        dataIsBinary = True
    try:
        baseString = baseBlob.content.decode('utf-8')
    except UnicodeDecodeError:
        dataIsBinary = True

    if dataIsBinary:
        printColor("Found conflict in file '{}'.".format(filename), "red")
        opt = None
        while opt not in ['t', 's', 'm', 'q']:
            print("========================================================================")
            print     (" <> Options:")
            print     ("    [t] --> Choose content of merge target.")
            print     ("    [s] --> Choose content of merge source.")
            printColor("    [q] --> Quit merging...", "red")
            print("========================================================================")
        if opt == 'q':
            printColor(" <> Aborting merge...", "red", "red")
            sys.exit(1)
        elif opt == 't':
            printColor(" <> '{}' file receives target content...".format(filename), "cyan")
            mergedContent = targetBlob.content
        elif opt == 's':
            printColor(" <> '{}' file receives source content...".format(filename), "cyan")
            mergedContent = sourceBlob.content
    else:
        mergedContent, hasConflict = merge(sourceString, targetString, baseString)

    if hasConflict and not dataIsBinary:
        printColor("Found conflict in file '{}'.".format(filename), "red")
        opt = None
        conflictSolved = False
        while not conflictSolved :
            while opt not in ['t', 's', 'm', 'q']:
                print("========================================================================")
                print     (" <> Options:")
                printColor("    [h] --> Show conflicting content.", "cyan")
                print     ("    [t] --> Choose content of merge target.")
                print     ("    [s] --> Choose content of merge source.")
                print     ("    [m] --> Manual conflict resolution.")
                printColor("    [q] --> Quit merging...", "red")
                print("========================================================================")
                opt = input("Please provide an option: ").lower()
                if opt not in ['t', 's', 'm', 'q']:
                    printColor("Please choose a valid option!", "red")
                if opt == 'h':
                    print(_unidiff_output(sourceString, targetString))
            if opt == 'q':
                printColor(" <> Aborting merge...", "red", "red")
                sys.exit(1)
            elif opt == 't':
                printColor(" <> '{}' file receives target content...".format(filename), "cyan")
                mergedContent = targetBlob.content
                conflictSolved = True
            elif opt == 's':
                printColor(" <> '{}' file receives source content...".format(filename), "cyan")
                mergedContent = sourceBlob.content
                conflictSolved = True
            elif opt == 'm':
                printColor("Resolving conflict for '{}'...".format(filename), "cyan")
                cacheFile(filename, cacheType="merge", fileContent=mergedContent.encode('utf-8'))
                fileEditProcess(os.path.join('.cookie', 'cache', 'merge_cache', filename))
                with open(os.path.join('.cookie', 'cache', 'merge_cache', filename), "r+b") as editedContent:
                    mergedContent=editedContent.read()
                try :
                    mergedContentStr = mergedContent.decode(encoding='utf-8')
                except:
                    printColor("Could not validate merged content, please choose another option!", "red")
                    continue
                if "<<<<<<<" in mergedContentStr and "=======" in mergedContentStr and ">>>>>>>" in mergedContentStr:
                    printColor("Found unsolved conflict, please resolve all conflicts or choose another option!", "red")
                else: 
                    conflictSolved = True
    metaData.append(mergedContent) 
    newBlob = Blob(b'?'.join(metaData))
    store(newBlob, objectsPath)
    return newBlob.getHash()

def mergeTrees(target, source, base, objectsPath): # the args are hashes
    if target == None and source==None and base == None:
        printColor("[DEV ERROR][mergeBlobs] all args None", "red")
    elif base == None:
        if target == None and source != None:
            return source
        elif target != None and source == None:
            return target
    if target == None:
        targetTree = Tree(None)
    else:
        targetTree=load(target, objectsPath)
    if source == None:
        sourceTree = Tree(None)
    else:
        sourceTree=load(source, objectsPath)
    if base == None:
        baseTree=Tree(None)
    else:
        baseTree=load(base, objectsPath)

    if targetTree.__class__.__name__!= "Tree" or sourceTree.__class__.__name__!= "Tree" or baseTree.__class__.__name__!= "Tree":
        printColor("[DEV ERROR][mergeTrees] Received a hash that is not a tree!", "red")
        sys.exit(1)
    for item in targetTree.map:
        objType = getObjectType(targetTree.map[item])
        targetArg=None
        sourceArg=None
        baseArg=None
        if item not in sourceTree.map:
            if item in baseTree.map:
                if targetTree.map[item]!= baseTree.map[item]:
                    # CONFLICT item modified in target & deleted in source
                    targetArg = targetTree.map[item]
                    baseArg = baseTree.map[item]
                else:
                    del targetTree.map[item] # ACTION item deleted in source ==> remove it from target
                    continue
            else:
                continue
                # OK item added since base in target but not in source, makes sense
        elif item in sourceTree.map:
            if targetTree.map[item] != sourceTree.map[item]:
                if item in baseTree.map:
                    # CONFLICT merge blobs or trees with base
                    targetArg = targetTree.map[item]
                    sourceArg = sourceTree.map[item]
                    baseArg = baseTree.map[item]
                else:
                    # CONFLICT merge blobs or trees with no base
                    targetArg = targetTree.map[item]
                    sourceArg = sourceTree.map[item]
            elif targetTree.map[item] == sourceTree.map[item]:
                continue
                # OK items are the same, alles gut
        else:
            printColor("[DEV ERROR][mergeTrees] what?", "red")
        if objType == 'T':
            targetTree.map[item]= mergeTrees(targetArg, sourceArg, baseArg, objectsPath)
        elif objType == 'B':
            targetTree.map[item] = mergeBlobs(targetArg, sourceArg, baseArg, objectsPath)
        else: 
            printColor("[DEV ERROR][mergeTrees] Found commit object in tree merging", "red")
            sys.exit(1)

    for item in sourceTree.map:
        # only for items in source that are not in target
        if item in targetTree.map:
            # case SHOULD have already been handled above
            continue
        else:
            if item in baseTree.map:
                # CONFLICT item was deleted in target yet it still exists in source
                objType = getObjectType(sourceTree.map[item], objectsPath)
                targetArg = None
                sourceArg = sourceTree.map[item]
                baseArg = baseTree.map[item]
            else:
                # OK item was added in source and is to be added in target
                targetTree.map[item] = sourceTree.map[item]
                continue
        if objType == 'T':
            targetTree.map[item]= mergeTrees(targetArg, sourceArg, baseArg, objectsPath)
        elif objType == 'B':
            targetTree.map[item] = mergeBlobs(targetArg, sourceArg, baseArg, objectsPath)
        else: 
            printColor("[DEV ERROR][mergeTrees] Found commit object in tree merging", "red")
            sys.exit(1)
    
    store(targetTree, objectsPath)
    return targetTree.getHash()

def createMergeCommit(target, source, commitToBranch=None):
    #check equality of target and source <TO DO>
    objectsPath = os.path.join(".cookie", "objects")
    #generateStatus(None,quiet=True)
    metaData=['C']
    refs=getResource("refs")
    head=getResource("head")
    targetIsHead=False
    targetIsBranchName=False
    if target in refs["B"]:
        targetSha = refs["B"][target]
        targetIsBranchName=True
        if target == head["name"]:
            targetIsHead=True
    else:
        targetSha=target
        if target == head["hash"]:
            targetIsHead = True
    targetTreeSha=getSnapshotFromCommit(targetSha, objectsPath)

    if getObjectType(targetSha, objectsPath) != 'C':
        printColor("Cannot merge into {} -- not a branch name or commit.".format(target), "red")

    if source in refs["B"]:
        sourceSha=refs["B"][source]
    else:
        sourceSha=source
    sourceTreeSha=getSnapshotFromCommit(sourceSha, objectsPath)
    if getObjectType(sourceSha, objectsPath) != 'C':
        printColor("Cannot merge from '{}' -- not a commit or a branch name".format(target), "red")
    mergeBase=getMergeBase(targetSha, sourceSha)

    if mergeBase == targetSha:
        opt=None
        while opt not in ['y', 'n', 'yes', 'no']:
            print("====================================================================")
            print(" <> Do you wish to update branch '{}' with new content? (y/n)".format(target))
            print("====================================================================")
            opt = input("Please provide an option: ").lower()
            if opt not in ['y', 'n', 'yes', 'no']:
                printColor("Please provide a valid option!", "red")
        if opt in ['y', 'yes']:
            if targetIsBranchName:
                refs['B'][target] = sourceSha
                if targetIsHead:
                    updateHead(target, currentRef=False, ref=sourceSha)
                    resetToSnapshot(sourceTreeSha, reset=True)
                dumpResource("refs", refs)
                printColor("Successfully merged changes to branch '{}'.".format(target), "green")
            else :
                printColor("Merge target must be a branch...", "red")
                #TO DO: what do we do if merge target is a commit hash? ignore?
                # depends if we commit all objects on push or just branch relevant ones!
                # i think we ignore? 23.4
    else:
        metaData.append(targetSha)
        metaData.append(sourceSha)
        baseTreeSha = getSnapshotFromCommit(mergeBase, objectsPath)
        targetTreeSha = mergeTrees(targetTreeSha, sourceTreeSha, baseTreeSha, objectsPath)
        
        metaData.append('A')
        userdata=getResource("userdata")    
        if userdata['user'] == "":
            printColor("Please login with a valid e-mail first!",'red')
            printColor("Use 'cookie login'",'white')
            sys.exit(0)
        else:
            metaData.append(userdata['user'])
            
        metaData.append("Merge into '{}' from '{}'".format(target, source))
        metaData.append(str(time()))
        metaData.append(targetTreeSha)
        newCommit = Commit('?'.join(metaData))
        opt=None
        while opt not in ['y', 'n', 'yes', 'no']:
            if commitToBranch:
                target = commitToBranch
                targetIsBranchName = True
            print("========================================================================")
            print(" <> Do you wish to commit merged content to branch '{}'? (y/n)".format(target))
            print("========================================================================")
            opt = input("Please provide an option: ").lower()
            if opt not in ['y', 'n', 'yes', 'no']:
                printColor("Please provide a valid option!", "red")
        if opt in ['y', 'yes']:
            store(newCommit, objectsPath)
            logCommit(newCommit)
            if targetIsBranchName:
                refs["B"][target] = newCommit.getHash()
                if targetIsHead:
                    updateHead(target, currentRef=False, ref=newCommit.getHash())
                    resetToSnapshot(newCommit.snapshot, reset=True)
            dumpResource("refs", refs)
            history = getResource("history")
            cacheFile(os.path.join(str(history["index"]+1), "new_commit"), cacheType="undo", fileContent=newCommit.getHash(), binary = False)
            printColor("Successfully committed merge to branch '{}'.".format(target), "green")

def getMergeBase(target, source):
    logs = getResource("logs")
    return findLCA([target],[source], logs)

def findLCA(a, b, graph):
    while a[-1] != b[-1]:
        if graph['nodes'][a[-1]] >= graph['nodes'][b[-1]]:
            if len(graph['adj'][a[-1]])==1:
                a.append(graph['edges'][str(graph['adj'][a[-1]][0])]['to'])
            else:
                a.append(findLCA(graph['edges'][str(graph['adj'][a[-1]][0])]['to'], graph['edges'][str(graph['adj'][a[-1]][1])]['to']))
        else:
            if len(graph['adj'][b[-1]])==1:
                b.append(graph['edges'][str(graph['adj'][b[-1]][0])]['to'])
            else:
                b.append(findLCA(graph['edges'][str(graph['adj'][b[-1]][0])]['to'], graph['edges'][str(graph['adj'][b[-1]][1])]['to']))
    return a[-1]


