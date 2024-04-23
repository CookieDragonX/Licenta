import os
from libs.objectLib.ObjectManager import load, getObjectType, getSnapshotFromCommit
from utils.prettyPrintLib import printColor
import sys
from errors.BranchExistsException import BranchExistsException
from errors.NoSuchObjectException import NoSuchObjectException
from libs.BasicUtils import statDictionary, getResource, dumpResource, safeWrite

def checkoutSnapshot(args):
    head=getResource("HEAD")
    if head["name"] == args.ref:
        printColor("Already on branch {}!".format(head["name"]), "blue")
        sys.exit(1)
    new_head='DETACHED'
    objectsPath = os.path.join('.cookie', 'objects')
    if args.ref == None:
        printColor("This does nothing, but is allowed. Give me some arguments!", "blue")
        sys.exit(0)
    refs=getResource("refs")
    if args.ref not in refs['B'] and args.ref not in refs['T']:
        try:
            objType=getObjectType(args.ref, objectsPath)
        except NoSuchObjectException as e:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("[DEV ERROR][checkoutSnapshot] That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)                                                                             #there's improvement to be done here
        snapshot=getSnapshotFromCommit(args.ref, objectsPath)                                       #get snapshot and raise notACommitError
        commitHash=args.ref
    else:
        try:
            if args.ref in refs['B']:
                printColor("Checking out branch {}...".format(args.ref), "green")
                commitHash=refs['B'][args.ref]
            elif args.ref in refs['T']:
                printColor("Checking out tag {}...".format(args.ref), "green")
                commitHash=refs['T'][args.ref]
            snapshot=getSnapshotFromCommit(commitHash, objectsPath)
            new_head=args.ref
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
                safeWrite(path, object.content)
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
    head=getResource("HEAD") 
    head["name"]=newHead
    if not currentRef:
        head["hash"]=ref
    dumpResource("HEAD", head)

def createBranch(branchName, currentRef=True, ref=None):
    head=getResource("HEAD")
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
        refs=getResource("refs")
        if branchName in refs["B"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException("Branch already exists")
        else:
            refs["B"][branchName]=ref
        dumpResource("refs", refs)
    except BranchExistsException as e:
        printColor("Cannot create a branch with name '{}' as one already exists", "red")

def updateBranchSnapshot():
    head=getResource("HEAD")
    refs=getResource("refs")
    refs["B"][head["name"]]=head["hash"]
    dumpResource("refs", refs)

def deleteBranch(branchName):
    head=getResource("HEAD")
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
        
    dumpResource("HEAD", head)
    dumpResource("refs", refs)