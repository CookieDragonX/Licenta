import json
import os
from libs.objectLib.ObjectManager import load, getObjectType, getSnapshotFromCommit
from utils.prettyPrintLib import printColor
import sys
from errors.BranchExistsException import BranchExistsException
from errors.NoSuchObjectException import NoSuchObjectException
from libs.BasicUtils import statDictionary

def checkoutSnapshot(args):
    new_head='DETACHED'
    objectsPath = os.path.join('.cookie', 'objects')
    if args.ref == None:
        printColor("This does nothing, but is allowed. Give me some arguments!", "blue")
        sys.exit(0)
    with open(os.path.join('.cookie', 'refs'), 'r') as refsFile:
        refs=json.load(refsFile)
    if args.ref not in refs['B'] and args.ref not in refs['T']:
        try:
            objType=getObjectType(args.ref, objectsPath)
        except NoSuchObjectException as e:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("[DEV ERROR][checkoutSnapshot] That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)                                                                             #there's improvement to be done here
        snapshot=getSnapshotFromCommit(args.ref, objectsPath)                                                    #get snapshot and raise notACommitError
    else:
        try:
            if args.ref in refs['B']:
                printColor("Checking out branch {}...".format(args.ref), "green")
                hash=refs['B'][args.ref]
            elif args.ref in refs['T']:
                printColor("Checking out tag {}...".format(args.ref), "green")
                hash=refs['T'][args.ref]
            snapshot=getSnapshotFromCommit(hash, objectsPath)
            new_head=args.ref
        except NoSuchObjectException as e:
            printColor("Could not find commit with hash {}".format(hash), "red")
            sys.exit(1)
    resetToSnapshot(snapshot)
    updateHead(new_head, currentRef=False, ref=snapshot)

def resetToSnapshot(hash, action='reset'):
    objectsPath = os.path.join('.cookie', 'objects')
    indexPath = os.path.join('.cookie', 'index')
    #with open(indexPath, 'r') as indexFile:
    index={}
    tree=load(hash, objectsPath)
    updateTree(tree, index, objectsPath, action)
    with open(indexPath, 'w') as indexFile:
        indexFile.seek(0)
        indexFile.write(json.dumps(index, indent=4))

def updateTree(tree,  index, objectsPath, action='reset'):
    for path, hash in tree.map.items():
        if action=='reset':
            object=load(hash, objectsPath)
            if object.__class__.__name__=='Blob':
                with open(path, 'w') as localObject:
                    localObject.write(object.content)
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
    headPath=os.path.join('.cookie', 'HEAD')
    with open(headPath, 'r') as headFile:
        head=json.load(headFile) 
    head["name"]=newHead
    if not currentRef:
        head["hash"]=ref
    with open(headPath, 'w') as headFile:
        headFile.seek(0)
        headFile.write(json.dumps(head, indent=4))
    if not currentRef:
        resetToSnapshot(ref)

def createBranch(branchName, currentRef=True, ref=None):
    try:
        if currentRef:
            with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
                head=json.load(headFile) 
                ref=head["hash"]
        if not currentRef :
            if ref==None:
                printColor("[DEV ERROR][createBranch] Method should take given ref but no ref given!", "red")
                sys.exit(1)
        with open(os.path.join('.cookie', 'refs'), 'r') as refsFile:
            refs=json.load(refsFile) 
        if branchName in refs["B"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException("Branch already exists")
        else:
            refs["B"][branchName]=ref
        with open(os.path.join('.cookie', 'refs'), 'w') as refsFile:
            refsFile.seek(0)
            refsFile.write(json.dumps(refs, indent=4))
    except BranchExistsException as e:
        printColor("Cannot create a branch with name '{}' as one already exists", "red")

def updateBranchSnapshot():
    with open(os.path.join(".cookie", "HEAD"), 'r') as headFile:
        head=json.load(headFile)
    with open(os.path.join(".cookie", "refs"), 'r') as refsFile:
        refs=json.load(refsFile) 
    refs["B"][head["name"]]=head["hash"]
    with open(os.path.join(".cookie", "refs"), 'w') as refsFile:
        refsFile.seek(0)
        refsFile.write(json.dumps(refs, indent=4))