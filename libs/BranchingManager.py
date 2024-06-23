import os
from libs.objectLib.ObjectManager import load, getObjectType, getSnapshotFromCommit
from utils.prettyPrintLib import printColor
import sys
from errors.NoSuchObjectException import NoSuchObjectException
from libs.BasicUtils import statDictionary, getResource, dumpResource, safeWrite
import shutil

def checkoutSnapshot(args, specRef = None, force=False, reset=False):
    refType=None
    if not specRef:
        ref = args.ref
    else :
        ref = specRef
    head=getResource("head")
    if head["name"] == ref and not force:
        printColor("Already on branch {}!".format(head["name"]), "cyan")
        printColor("Use checkout with 'f' flag to force checkout...", "cyan")
        sys.exit(1)
    new_head='DETACHED'
    objectsPath = os.path.join('.cookie', 'objects')
    if ref == None:
        printColor("Please provide the reference point to checkout!", "cyan")
        sys.exit(1)
    refs=getResource("refs")
    if ref not in refs['B'] and ref not in refs['T']:
        try:
            objType=getObjectType(ref, objectsPath)
        except NoSuchObjectException as e:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("[DEV ERROR][checkoutSnapshot] That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)
        snapshot=getSnapshotFromCommit(ref, objectsPath)
        commitHash=ref
    else:
        try:
            if ref in refs['B']:
                refType='B'
                printColor("Checking out branch {}...".format(ref), "green")
                commitHash=refs['B'][ref]
            elif ref in refs['T']:
                refType='T'
                printColor("Checking out tag {}...".format(ref), "green")
                commitHash=refs['T'][ref]
            snapshot=getSnapshotFromCommit(commitHash, objectsPath)
            new_head=ref
        except NoSuchObjectException as e:
            printColor("Could not find commit with hash {}".format(commitHash), "red")
            sys.exit(1)
    resetToSnapshot(snapshot, reset)
    updateHead(new_head, currentRef=False, ref=commitHash, tag=(refType=='T'))
    printColor("    <> Current commit hash: '{}'".format(commitHash), "green" )
    history = getResource("history")
    try:
        shutil.move(os.path.join(".cookie", "cache", "index_cache"), os.path.join(".cookie", "cache", "undo_cache", str(history["index"]+1), "index_cache"))
    except FileNotFoundError:
        # checkout one after another, index_cache missing at that moment
        pass

def resetToSnapshot(hash, reset=False):
    objectsPath = os.path.join('.cookie', 'objects')
    index={}
    tree=load(hash, objectsPath)
    updateTree(tree, index, objectsPath, reset=reset)
    dumpResource("index", index)
    
def updateTree(tree, index, objectsPath, reset):
    if tree.__class__.__name__!='Tree':
        printColor("[DEV ERROR][updateTree] Method received object that is not tree: {}".format(tree.__class__.__name__), "red")
        printColor("hash: {}".format(tree.getHash()),"red")
        sys.exit(1)
    for path, hash in tree.map.items():
        object=load(hash, objectsPath)
        if object.__class__.__name__=='Blob':
            try:
                with open(path, "rb") as file:
                    currentContent = file.read()
                if object.content != currentContent:
                    if reset:
                        safeWrite(path, object.content, binary=True)
                        mode = os.lstat(path)
                        index[path] = statDictionary(mode)
                    else:
                        index[path] = statDictionary(None)
                    index[path]['hash'] = hash
                else:
                    mode = os.lstat(path)
                    index[path] = statDictionary(mode)
                    index[path]['hash'] = hash
            except FileNotFoundError:
                if reset:   
                    safeWrite(path, object.content, binary=True)
                    mode = os.lstat(path)
                    index[path] = statDictionary(mode)
                else:
                    index[path] = statDictionary(None)
                index[path]['hash'] = hash
        elif object.__class__.__name__=='Tree':
            updateTree(object, index, objectsPath, reset)
        else:
            print("[DEV ERROR][updateTree] Found a commit hash in a tree probably?")
            
def updateHead(newHead, currentRef=True, ref=None, tag=False):
    head=getResource("head") 
    head["name"]=newHead
    if not currentRef:
        head["hash"]=ref
    head["tag"] = False
    if tag:
        head["tag"]=True
    dumpResource("head", head)

def createBranch(branchName, currentRef=True, ref=None, checkout=False):
    head=getResource("head")
    if head["hash"]=="":
        printColor("Please commit something before creating branches!", "red")
        printColor("Merging won't be possible if branches start from different commits!", "red")
        sys.exit(1)
    if branchName == "DETACHED":
        printColor("Cannot name branch 'DETACHED' as name is used as ref point state...", "red")
        sys.exit(1)
    if currentRef:
        ref=head["hash"]
    if not currentRef :
        if ref==None:
            printColor("[DEV ERROR][createBranch] Method should take given ref but no ref given!", "red")
            sys.exit(1)
    refs=getResource("refs")
    if branchName in refs["T"].keys():
        printColor("Tag name '{}' already exists!".format(branchName), "red")
        sys.exit(1)
    elif branchName in refs["B"].keys():
        printColor("Branch name '{}' already exists!".format(branchName), "red")
        sys.exit(1)
    else:
        refs["B"][branchName]=ref
    dumpResource("refs", refs)
    if checkout:
        checkoutSnapshot(None, specRef=branchName, force=True)

def createTag(tagName, currentRef=True, ref=None, checkout=False):
    head=getResource("head")
    if head["hash"]=="":
        printColor("Please commit something before creating tags!", "red")
        sys.exit(1)
    if tagName == "DETACHED":
        printColor("Cannot name tag 'DETACHED' as name is used as ref point state...", "red")
        sys.exit(1)
    if currentRef:
        ref=head["hash"]
    if not currentRef :
        if ref==None:
            printColor("[DEV ERROR][createTag] Method should take given ref but no ref given!", "red")
            sys.exit(1)
    refs=getResource("refs")
    if tagName in refs["T"].keys():
        printColor("Tag name '{}' already exists!".format(tagName), "red")
        sys.exit(1)
    elif tagName in refs["B"].keys():
        printColor("Branch name '{}' already exists!".format(tagName), "red")
        sys.exit(1)
    else:
        refs["T"][tagName]=ref
    dumpResource("refs", refs)
    if checkout:
        checkoutSnapshot(None, specRef=tagName, force=True)



def updateBranchSnapshot():
    head=getResource("head")
    refs=getResource("refs")
    refs["B"][head["name"]]=head["hash"]
    dumpResource("refs", refs)

def deleteBranch(branchName):
    head=getResource("head")
    refs=getResource("refs") 
    if branchName not in refs['B']:
        printColor("No such branch to be deleted {}".format(branchName))
        sys.exit(1)
    undoInfo=refs['B'][branchName]
    if head["name"]==branchName:
        head["name"] = "DETACHED"
    refs['D'][branchName] = refs['B'][branchName]
    del refs['B'][branchName]
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "branches")
    os.makedirs(undoCachePath, exist_ok=True)
    safeWrite(os.path.join(undoCachePath, branchName), undoInfo)
        
    dumpResource("head", head)
    dumpResource("refs", refs)

def deleteTag(tagName):
    head=getResource("head")
    refs=getResource("refs") 
    if tagName not in refs['T']:
        printColor("No such branch to be deleted {}".format(tagName))
        sys.exit(1)
    undoInfo=refs['T'][tagName]
    if head["name"]==tagName:
        head["name"] = "DETACHED"
    refs['D'][tagName] = refs['T'][tagName]
    del refs['T'][tagName]
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "tags")
    os.makedirs(undoCachePath, exist_ok=True)
    safeWrite(os.path.join(undoCachePath, tagName), undoInfo)
        
    dumpResource("head", head)
    dumpResource("refs", refs)
