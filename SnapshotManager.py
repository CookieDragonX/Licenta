import json
import os
from ObjectManager import load
from prettyPrintLib import printColor


def getSnapshotFromCommit(hash):
    commit=load(hash, os.path.join('.cookie', 'objects'))
    return commit.snapshot

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
    