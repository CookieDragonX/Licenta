import os
from libs.objectLib.ObjectManager import load, getObjectType, getSnapshotFromCommit
from utils.prettyPrintLib import printColor
import sys
from errors.BranchExistsException import BranchExistsException
from errors.NoSuchObjectException import NoSuchObjectException
from libs.BasicUtils import statDictionary, getResource, dumpResource, safeWrite

def checkoutSnapshot(args, specRef = None, force=False):
    if not specRef:
        ref = args.ref
    else :
        ref = specRef
    head=getResource("head")
    if head["name"] == ref and not force:
        printColor("Already on branch {}!".format(head["name"]), "blue")
        sys.exit(1)
    new_head='DETACHED'
    objectsPath = os.path.join('.cookie', 'objects')
    if ref == None:
        printColor("This does nothing, but is allowed. Give me some arguments!", "blue")
        sys.exit(0)
    refs=getResource("refs")
    if ref not in refs['B'] and ref not in refs['T']:
        try:
            objType=getObjectType(ref, objectsPath)
        except NoSuchObjectException as e:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("[DEV ERROR][checkoutSnapshot] That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)                                                                             #there's improvement to be done here
        snapshot=getSnapshotFromCommit(ref, objectsPath)                                       #get snapshot and raise notACommitError
        commitHash=ref
    else:
        try:
            if ref in refs['B']:
                printColor("Checking out branch {}...".format(ref), "green")
                commitHash=refs['B'][ref]
            elif ref in refs['T']:
                printColor("Checking out tag {}...".format(ref), "green")
                commitHash=refs['T'][ref]
            snapshot=getSnapshotFromCommit(commitHash, objectsPath)
            new_head=ref
        except NoSuchObjectException as e:
            printColor("Could not find commit with hash {}".format(commitHash), "red")
            sys.exit(1)
    resetToSnapshot(snapshot)
    updateHead(new_head, currentRef=False, ref=commitHash)

def resetToSnapshot(hash, action='reset'):
    objectsPath = os.path.join('.cookie', 'objects')
    index={}
    tree=load(hash, objectsPath)
    updateTree(tree, index, objectsPath, action)
    dumpResource("index", index)

def updateTree(tree, index, objectsPath, action='reset'):
    if tree.__class__.__name__!='Tree':
        printColor("[DEV ERROR][updateTree] Method received object that is not tree: {}".format(tree.__class__.__name__), "red")
        printColor("hash: {}".format(tree.getHash()),"red")
        sys.exit(1)
    for path, hash in tree.map.items():
        if action=='reset':
            object=load(hash, objectsPath)
            if object.__class__.__name__=='Blob':
                safeWrite(path, object.content, binary=True)
                mode = os.lstat(path)
                index[path]=statDictionary(mode)
                index[path]['hash'] = hash
            elif object.__class__.__name__=='Tree':
                updateTree(object, index, objectsPath, action)
            else:
                print("[DEV ERROR][resetToSnapshot] Found a commit hash in a tree probably?")
        elif action=='merge':
            #logic for merging changes with commit that gets checked out
            pass
        else:
            printColor("[DEV ERROR][resetToSnapshot] action undefined {}".format(action), 'red')
    
def updateHead(newHead, currentRef=True, ref=None):
    head=getResource("head") 
    head["name"]=newHead
    if not currentRef:
        head["hash"]=ref
    dumpResource("head", head)

def createBranch(branchName, currentRef=True, ref=None, checkout=False):
    head=getResource("head")
    if head["hash"]=="":
        printColor("Please commit something before creating branches!", "red")
        printColor("Merging won't be possible if branches start from different commits!", "red")
        sys.exit(1)
    try:
        if currentRef:
            ref=head["hash"]
        if not currentRef :
            if ref==None:
                printColor("[DEV ERROR][createBranch] Method should take given ref but no ref given!", "red")
                sys.exit(1)
        elif checkout:
            checkoutSnapshot(None, ref)
        refs=getResource("refs")
        if branchName in refs["B"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException("Branch already exists")
        else:
            refs["B"][branchName]=ref
        dumpResource("refs", refs)
    except BranchExistsException as e:
        printColor("Cannot create a branch with name '{}' as one already exists", "red")

def createTag(tagName, currentRef=True, ref=None, checkout=False):
    head=getResource("head")
    if head["hash"]=="":
        printColor("Please commit something before creating tags!", "red")
        sys.exit(1)
    try:
        if currentRef:
            ref=head["hash"]
        if not currentRef :
            if ref==None:
                printColor("[DEV ERROR][createTag] Method should take given ref but no ref given!", "red")
                sys.exit(1)
            elif checkout:
                checkoutSnapshot(None, ref)
        refs=getResource("refs")
        if tagName in refs["T"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException("Tag already exists")
        else:
            refs["T"][tagName]=ref
        dumpResource("refs", refs)
    except BranchExistsException as e:
        printColor("Cannot create a tag with name '{}' as one already exists", "red")


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
    del refs['T'][tagName]
    undoCachePath=os.path.join(".cookie", "cache", "undo_cache", "branches")
    os.makedirs(undoCachePath, exist_ok=True)
    safeWrite(os.path.join(undoCachePath, tagName), undoInfo)
        
    dumpResource("head", head)
    dumpResource("refs", refs)