from errors.NoSuchObjectException import NoSuchObjectException
import os
from hashlib import sha1 
from libs.objectLib.Blob import Blob
from libs.objectLib.Tree import Tree
from libs.objectLib.Commit import Commit
from libs.BasicUtils import safeWrite

def load(hash, objectsPath):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException("No such object!")
    else:
        with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'rb') as object:
            metaData=object.read()
        metaData=metaData.decode(encoding='utf-8')
        objectType=metaData.split('?')[0]
        if objectType=='B':
            return Blob(metaData)
        elif objectType=='C':
            return Commit(metaData)
        elif objectType=='T':
            return Tree(metaData)
    return None

def store(object, objectsPath):
    id=object.getHash()
    if not os.path.isdir(os.path.join(objectsPath, id[:2])):
        os.mkdir(os.path.join(objectsPath, id[:2]))
    safeWrite(os.path.join(objectsPath, id[:2], id[2:]), object.getMetaData(), binary=True)

def getHash(path): #only Blob but not really an useful method
    with open(path, 'r') as fp:
        fileContent=fp.read()
    blobContent='?'.join(['B', path, fileContent])
    return sha1(blobContent.encode(encoding='utf-8'))

def createBlob(path):
    with open(path, 'r') as fp:
        fileContent=fp.read()
    metaData='?'.join(['B', path, fileContent])
    return Blob(metaData)

def getObjectType(hash, objectsPath):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException("No such object!")
    with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'rb') as object:
        metaData=object.read()
    metaData=metaData.decode(encoding='utf-8')
    return metaData.split('?')[0]

def getMetaData(hash,objectsPath):
    with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'r') as object:
        return object.read().decode(encoding='utf-8')
    
def hashTree(dir, objectsPath):
    metaData=['T']
    for pathname in os.listdir(dir):
        if os.path.isdir(pathname):
            treeHash=hashTree(dir)
            metaData.extend([pathname, treeHash])
        elif os.path.isfile(pathname):
            metaData.extend([pathname, getHash(pathname)])
    tree=Tree('?'.join(metaData))
    store(tree, objectsPath)
    return tree.getHash()

def getSnapshotFromCommit(hash, objectsPath):
    commit=load(hash, objectsPath)
    return commit.snapshot
