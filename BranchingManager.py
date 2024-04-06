import json
import os
from objectLib.ObjectManager import load, getObjectType, getSnapshotFromCommit
from utils.prettyPrintLib import printColor
import sys
from errors import BranchExistsException, NoSuchObjectException

def checkoutSnapshot(args):
    new_head='DETACHED'
    if args.ref == None:
        printColor("This does nothing, but is allowed. Give me some arguments!", "blue")
        sys.exit(0)
    with open(os.path.join('.cookie', 'refs'), 'r') as refsFile:
        refs=json.load(refsFile)
    if args.ref not in refs['B'] and args.ref not in refs['T']:
        try:
            objType=getObjectType(args.ref)
        except NoSuchObjectException:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)                                                                             #there's improvement to be done here
        snapshot=getSnapshotFromCommit(args.ref)                                                    #get snapshot and raise notACommitError
    else:
        try:
            if args.ref in refs['B']:
                printColor("Checking out branch {}...".format(args.ref), "green")
                hash=refs['B'][args.ref]
            elif args.ref in refs['T']:
                printColor("Checking out tag {}...".format(args.ref), "green")
                hash=refs['T'][args.ref]
            snapshot=getSnapshotFromCommit(hash)
            new_head=args.ref
        except NoSuchObjectException:
            printColor("Could not find commit with hash {}".format(hash), "red")
            sys.exit(1)
    resetToSnapshot(snapshot)
    updateHead(new_head)

def resetToSnapshot(hash, action='reset'):
    objectsPath = os.path.join('.cookie', 'objects')
    indexPath = os.path.join('.cookie', 'index')
    tree=load(hash, objectsPath)
    with open(indexPath, 'r') as indexFile:
        index=json.load(indexFile)
    for path, hash in tree.map.items():
        if action=='reset':
            blob=load(hash, objectsPath)
            with open(path, 'w') as localObject:
                localObject.write(blob.content)
            index[path]['hash'] = hash
        elif action=='merge':
            #logic for merging changes with commit that gets checked out
            pass
        else:
            printColor("wtf this should never happen", 'red')
    with open(indexPath, 'w') as indexFile:
        indexFile.seek(0)
        indexFile.write(json.dumps(index, indent=4))
    
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
                printColor("This should never happen, pls debug if it did", "red")
                sys.exit(1)
        with open(os.path.join('.cookie', 'refs'), 'r') as refsFile:
            refs=json.load(refsFile) 
        if branchName in refs["B"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException
        else:
            refs["B"][branchName]=ref
        with open(os.path.join('.cookie', 'refs'), 'w') as refsFile:
            refsFile.seek(0)
            refsFile.write(json.dumps(refs, indent=4))
    except BranchExistsException:
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