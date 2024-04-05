import json
import os
from ObjectManager import load, getObjectType, getSnapshotFromCommit
from prettyPrintLib import printColor
import sys
from errors import BranchExistsException, NoSuchObjectException

def checkoutSnapshot(args):
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
        if args.ref in refs['B']:
            printColor("Checking out branch {}...".format(args.refs), "green")
            snapshot=getSnapshotFromCommit(refs['B'][args.ref])
        if args.ref in refs['T']:
            printColor("Checking out tag {}...".format(args.refs), "green")
            snapshot=getSnapshotFromCommit(refs['T'][args.ref])
    resetToSnapshot(snapshot)

def resetToSnapshot(hash, action='reset'):
    objectsPath = os.path.join('.cookie', 'objects')
    indexPath = os.path.join('.cookie', 'index')
    tree=load(hash, objectsPath)
    with open(indexPath, 'r') as indexFile:
        index=json.loads(indexFile)
    for path, hash in tree.map.items():
        if action=='reset':
            object=load(hash, objectsPath)
            with open(path, 'w') as localObject:
                localObject.write(object.getMetaData())
            index[path] = hash
        elif action=='merge':
            #logic for merging changes with commit that gets checked out
            pass
        else:
            printColor("wtf this should never happen", 'red')
    with open(indexPath, 'w') as indexFile:
        indexFile.write(json.dumps(index, indent=4))
    
def updateHead(newHead):
    with open(os.path.join('.cookie', 'HEAD'), 'r+') as headFile:
        head=json.load(headFile) 
        head["name"]=newHead
        headFile.write(json.dumps(head, indent=4))

def createBranch(branchName, currentRef=True, ref=""):
    if currentRef:
        with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
            head=json.load(headFile) 
            ref=head["hash"]
    if not currentRef :
        if ref=="":
            printColor("This should never happen, pls debug if it did", "red")
            sys.exit(1)
    with open(os.path.join('.cookie', 'refs'), 'r+') as refsFile:
        refs=json.load(refsFile) 
        if branchName in refs["B"].keys():
            #printColor("Branch name '{}' already exists!".format(branchName), "red")
            raise BranchExistsException
        else:
            refs["B"][branchName]=ref
        refsFile.write(json.dumps(refs, indent=4))